"""Static scientific figures for the saved offline development analysis."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

COLORS={'additive':'#2678b2','pairwise':'#d26728'}


def plot(output, analysis, residuals, historical):
    plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
    def save(fig,name):
        fig.savefig(output/(name+'.png'),dpi=180,bbox_inches='tight')
        fig.savefig(output/(name+'.svg'),bbox_inches='tight')
        plt.close(fig)

    fig,axes=plt.subplots(1,3,figsize=(13,4),layout='constrained')
    for ax,scope,title in zip(axes[:2],('development','historical_evaluation'),
                              ('Historical development fit (51)','Historical evaluation (13; previously seen)')):
        selected=[r for r in residuals if r['split']==scope]
        for model in COLORS:
            ax.scatter([r['target_ev']*1000 for r in selected],[r[model+'_prediction_ev']*1000 for r in selected],
                       s=22,alpha=.8,label=model,color=COLORS[model])
        ax.plot([-100,200],[-100,200],color='gray',ls='--',lw=1)
        ax.set(xlabel='Saved four-start UMA score (meV)',ylabel='Predicted score (meV)',title=title)
        ax.legend()
    cv=[r for r in analysis['cv'] if r['method']=='repeated_group_kfold']
    for i,model in enumerate(COLORS):
        values=[r['metrics'][model]['mae_ev']*1000 for r in cv if r['metrics'][model]['count']==51]
        axes[2].scatter(np.full(len(values),i),values,s=18,alpha=.5,color=COLORS[model])
        axes[2].plot([i-.13,i+.13],[analysis['cv'][0]['metrics'][model]['mae_ev']*1000]*2,color='black',lw=2)
    axes[2].set(xticks=[0,1],xticklabels=list(COLORS),ylabel='Development OOF MAE (meV)',
                title='20 grouped 5-fold repetitions\nBlack line: leave-one-group-out')
    fig.suptitle('Fixed-label fitting diagnostics; no independent physical validation',fontsize=12)
    save(fig,'fit_and_grouped_cv')

    ordered=sorted(residuals,key=lambda r:(r['amino_count'],r['pattern']))
    values=[]
    for r in ordered:
        suffix='_logo_residual_ev' if r['split']=='development' else '_residual_ev'
        values.append([np.nan if r[m+suffix] is None else 1000*r[m+suffix] for m in COLORS])
    fig,(ax,ax2)=plt.subplots(1,2,figsize=(10,12),gridspec_kw={'width_ratios':[1,2]},layout='constrained')
    limit=np.nanmax(np.abs(values))
    heat=ax.imshow(values,cmap='RdBu_r',vmin=-limit,vmax=limit,aspect='auto')
    ax.set(xticks=[0,1],xticklabels=list(COLORS),yticks=range(64),
           yticklabels=[r['pattern']+('  H' if r['split']=='historical_evaluation' else '') for r in ordered],
           title='Exact pattern residuals\nH = historical evaluation')
    ax.tick_params(axis='y',labelsize=7)
    fig.colorbar(heat,ax=ax,label='Prediction − saved target (meV)',shrink=.5)
    for model,offset in zip(COLORS,(-.08,.08)):
        dev=[r for r in residuals if r['split']=='development' and r[model+'_logo_residual_ev'] is not None]
        ax2.scatter([r['amino_count']+offset for r in dev],[1000*r[model+'_logo_residual_ev'] for r in dev],
                    color=COLORS[model],s=30,alpha=.65,label=model)
    ax2.axhline(0,color='gray',lw=1)
    ax2.set(xlabel='Amino count',ylabel='Leave-group-out residual (meV)',xticks=range(7),
            title='Development only; groups stay together\nCounts 0 and 6 each have one design')
    ax2.legend()
    fig.suptitle('Residual structure: development OOF and historical evaluation kept distinct',fontsize=12)
    save(fig,'residual_patterns')

    fig,axes=plt.subplots(1,2,figsize=(11,7),layout='constrained')
    terms=['offset']+[f'h{i}' for i in range(6)]+[f'J{i}{j}' for i in range(6) for j in range(i+1,6)]
    for ax,model in zip(axes,COLORS):
        s=analysis['stability'][model]
        q=np.array(s['coefficient_percentiles_2_5_50_97_5_ev'])*1000
        n=q.shape[1];y=np.arange(n)
        ax.hlines(y,q[0],q[2],color=COLORS[model],lw=2)
        ax.scatter(np.array(analysis['full_coefficients_ev'][model])*1000,y,color='black',s=18,label='Full development OLS')
        ax.axvline(0,color='gray',ls='--',lw=1)
        ax.set(yticks=y,yticklabels=terms[:n],xlabel='Coefficient (meV)',
               title=f'{model}: {s["identifiable"]}/{s["attempted"]} identifiable draws')
        ax.invert_yaxis();ax.legend(loc='lower left',fontsize=8)
    fig.suptitle('Whole-group bootstrap 2.5–97.5% ranges; conditional stability, not physical confidence',fontsize=11)
    save(fig,'coefficient_stability')

    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for ax,model in zip(axes,COLORS):
        q=np.array(analysis['stability'][model]['rank_percentiles_5_50_95'])
        order=np.argsort(q[1],kind='stable')
        ax.vlines(np.arange(len(order)),q[0,order],q[2,order],color=COLORS[model],alpha=.7)
        ax.scatter(np.arange(len(order)),q[1,order],color=COLORS[model],s=12)
        ticks=np.arange(0,len(order),5)
        ax.set(xticks=ticks,xticklabels=[analysis['ids'][order[i]][-6:] for i in ticks],
               xlabel='Development patterns ordered by median rank',ylabel='Predicted rank (lower preferred)',
               title=model+'; 5–95% bootstrap rank ranges',ylim=(52,0))
        ax.tick_params(axis='x',rotation=60)
    fig.suptitle('Ranking stability on the 51 development patterns only; no material-ranking claim',fontsize=11)
    save(fig,'development_rank_stability')

    fig,(ax,ax2)=plt.subplots(1,2,figsize=(12,4),layout='constrained')
    sample=analysis['sampling_sensitivity']['records']
    for key,color in [('CO2','#2678b2'),('H2O','#d26728'),('delta','#4c956c')]:
        values=np.array([r[key+'_four_minus_two_ev'] for r in sample])*1000
        ax.plot(np.sort(values),label=key,color=color,lw=1.6)
    ax.axhline(0,color='gray',lw=1)
    ax.set(xlabel='Development designs sorted separately per series',ylabel='Four-start − two-start value (meV)',
           title='Nested-start sensitivity, common bare reference')
    ax.legend()
    lookup={r['id']:r for r in residuals}
    for model in COLORS:
        valid=[r for r in sample if lookup[r['id']][model+'_logo_residual_ev'] is not None]
        ax2.scatter([abs(r['delta_four_minus_two_ev'])*1000 for r in valid],
                    [abs(lookup[r['id']][model+'_logo_residual_ev'])*1000 for r in valid],
                    color=COLORS[model],s=25,alpha=.65,label=model)
    ax2.set(xlabel='Absolute paired-target sampling change (meV)',ylabel='Absolute development OOF residual (meV)',
            title='Descriptive relationship; no variance attribution')
    ax2.legend()
    fig.suptitle('Fitting error and sampled-target sensitivity are different quantities',fontsize=12)
    save(fig,'sampling_vs_fitting')
