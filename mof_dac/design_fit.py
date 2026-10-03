"""Grouped, label-independent splits and provisional quadratic diagnostics."""

import numpy as np

from mof_dac.parameters import fit_pairwise, pairwise_design


def freeze_split(states, group_lists, seed=41, development_ids=('uio66_000000', 'uio66_111111')):
    """Merge duplicate graphs, reserve pilot groups for training, hold out 20%."""
    adjacency = {identifier: set() for identifier in states}
    for groups in group_lists:
        flattened = [identifier for group in groups for identifier in group]
        if len(flattened) != len(states) or set(flattened) != set(states):
            raise ValueError('Duplicate audit must cover every state exactly once')
        for group in groups:
            for identifier in group[1:]:
                adjacency[group[0]].add(identifier)
                adjacency[identifier].add(group[0])
    groups, unseen = [], set(states)
    while unseen:
        pending, component = [min(unseen)], set()
        while pending:
            identifier = pending.pop()
            if identifier in component:
                continue
            component.add(identifier)
            pending.extend(adjacency[identifier] - component)
        unseen -= component
        groups.append(sorted(component))
    eligible = [i for i, group in enumerate(groups) if not set(group).intersection(development_ids)]
    rng = np.random.default_rng(seed)
    test_groups = set(rng.permutation(eligible)[:int(np.ceil(0.2*len(groups)))].tolist())
    if not test_groups or len(test_groups) == len(groups):
        raise ValueError('Insufficient independent groups')
    train = sorted(identifier for i, group in enumerate(groups) if i not in test_groups for identifier in group)
    test = sorted(identifier for i, group in enumerate(groups) if i in test_groups for identifier in group)
    design = pairwise_design([states[identifier] for identifier in train])
    rank = int(np.linalg.matrix_rank(design))
    if rank != design.shape[1]:
        raise ValueError(f'Frozen training design unidentifiable: {rank}/{design.shape[1]}')
    return {'seed': seed, 'policy': '20% merged duplicate groups; development pilot groups train-only; labels unused',
        'groups': groups, 'train_ids': train, 'test_ids': test, 'training_design_rank': rank}


def evaluate_fit(states, targets, split, bootstrap=200):
    """OLS additive/pairwise holdout comparison; training-group bootstrap only."""
    if not isinstance(bootstrap, int) or bootstrap < 0:
        raise ValueError('Bootstrap count must be a nonnegative integer')
    if set(states) != set(targets) or set(split['train_ids'] + split['test_ids']) != set(states):
        raise ValueError('Every frozen configuration needs one complete target')
    if any(value is None or not np.isfinite(value) for value in targets.values()):
        raise ValueError('Incomplete/nonfinite targets cannot be fit')
    train, test = split['train_ids'], split['test_ids']
    if len(set(train)) != len(train) or len(set(test)) != len(test) or set(train).intersection(test):
        raise ValueError('Train/test identities must be unique and disjoint')
    for group in split['groups']:
        if set(group).intersection(train) and set(group).intersection(test):
            raise ValueError('Duplicate group crosses train/test boundary')
    x = np.array([states[k] for k in train], float)
    y = np.array([targets[k] for k in train], float)
    xt = np.array([states[k] for k in test], float)
    yt = np.array([targets[k] for k in test], float)
    if not np.isin(np.vstack([x, xt]), [0, 1]).all():
        raise ValueError('Binary substitution states required')
    pairwise = fit_pairwise(x, y)
    design, test_design = pairwise_design(x), pairwise_design(xt)
    weights = np.r_[pairwise['offset'], pairwise['h'], pairwise['W'][np.triu_indices(x.shape[1], 1)]]
    additive_weights = np.linalg.lstsq(design[:, :x.shape[1]+1], y, rcond=None)[0]

    def metrics(prediction, truth):
        error = prediction-truth
        return {'mae_ev': float(np.mean(np.abs(error))), 'rmse_ev': float(np.sqrt(np.mean(error**2))),
                'max_absolute_error_ev': float(np.max(np.abs(error)))}

    train_set = set(train)
    groups = [group for group in split['groups'] if set(group) <= train_set]
    index = {identifier: i for i, identifier in enumerate(train)}
    rng, samples = np.random.default_rng(split['seed']), []
    for _ in range(bootstrap):
        selected = [index[k] for i in rng.integers(len(groups), size=len(groups)) for k in groups[i]]
        matrix = design[selected]
        if np.linalg.matrix_rank(matrix) == matrix.shape[1]:
            samples.append(np.linalg.lstsq(matrix, y[selected], rcond=None)[0])
    uncertainty = {'method': 'training-group bootstrap; conditional on this sampled UMA target',
        'attempted': bootstrap, 'identifiable_replicates': len(samples),
        'physical_model_and_sampling_uncertainty': 'not calibrated; independently unresolved'}
    if len(samples) >= 2:
        uncertainty['coefficient_std_ev'] = np.std(samples, axis=0, ddof=1).tolist()
        uncertainty['coefficient_percentiles_2_5_97_5_ev'] = np.percentile(samples, [2.5, 97.5], axis=0).tolist()
    return {'status': 'provisional model fit; not independently validated chemistry',
        'train_count': len(train), 'test_count': len(test), 'parameters': len(weights),
        'rank': pairwise['rank'], 'condition_number': float(np.linalg.cond(design)),
        'offset_ev': pairwise['offset'], 'h_ev': pairwise['h'].tolist(), 'W_ev': pairwise['W'].tolist(),
        'pairwise_train': metrics(design @ weights, y), 'pairwise_test': metrics(test_design @ weights, yt),
        'additive_train': metrics(design[:, :x.shape[1]+1] @ additive_weights, y),
        'additive_test': metrics(test_design[:, :x.shape[1]+1] @ additive_weights, yt),
        'uncertainty': uncertainty,
        'heldout_predictions': [{'id': k, 'target_ev': float(truth), 'pairwise_ev': float(pair),
            'additive_ev': float(add)} for k, truth, pair, add in zip(test, yt, test_design @ weights,
                test_design[:, :x.shape[1]+1] @ additive_weights)]}
