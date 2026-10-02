"""Optional Gurobi reference for the original constrained binary problem."""

from time import perf_counter

import numpy as np

from .optimizers import Result


def solve_gurobi(problem, *, time_limit=60.0, seed=0, threads=1):
    """Solve binary x with raw H, E@x=e and U@x<=u; report bound/status."""
    if time_limit <= 0 or threads < 1:
        raise ValueError("Require positive time limit and thread count")
    try:
        import gurobipy as gp
        from gurobipy import GRB
    except ImportError as error:
        raise ImportError('Install optional integration with pip install -e ".[gurobi]"') from error
    start = perf_counter()
    try:
        model = gp.Model("mof_dac_reference")
        model.Params.OutputFlag = 0
        model.Params.TimeLimit = time_limit
        model.Params.Seed = seed
        model.Params.Threads = threads
        model.Params.NonConvex = 2
        x = model.addMVar(problem.n, vtype=GRB.BINARY, name="x")
        model.setObjective(x @ problem.binary_qubo() @ x, GRB.MINIMIZE)
        if len(problem.e):
            model.addConstr(problem.E @ x == problem.e, name="eq")
        if len(problem.u):
            model.addConstr(problem.U @ x <= problem.u, name="le")
        model.optimize()
        names = {GRB.OPTIMAL: "optimal", GRB.TIME_LIMIT: "time_limit",
                 GRB.INFEASIBLE: "infeasible", GRB.INF_OR_UNBD: "infeasible_or_unbounded",
                 GRB.INTERRUPTED: "interrupted"}
        status = names.get(model.Status, f"gurobi_status_{model.Status}")
        solution = np.asarray(x.X, dtype=float) if model.SolCount else None
        diagnostics = {"gurobi_version": ".".join(map(str, gp.gurobi.version())),
                       "status_code": int(model.Status), "solution_count": int(model.SolCount),
                       "best_bound": float(model.ObjBound) if model.SolCount else None,
                       "mip_gap": float(model.MIPGap) if model.SolCount else None,
                       "nodes": float(model.NodeCount), "runtime": float(model.Runtime),
                       "time_limit": float(time_limit), "seed": int(seed),
                       "threads": int(threads), "nonconvex_parameter": 2}
        return Result("gurobi_reference", solution, perf_counter() - start, status, diagnostics)
    except gp.GurobiError as error:
        return Result("gurobi_reference", None, perf_counter() - start, "gurobi_error",
                      {"error_code": int(error.errno), "message": str(error)})
