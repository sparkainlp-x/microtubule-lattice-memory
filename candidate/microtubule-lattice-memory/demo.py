"""Demo for microtubule-lattice-memory v0.1.0. Run: python demo.py
Writes results.json in this directory.
"""
import json

from experiments import run_all


def main():
    res = run_all()
    print("microtubule-lattice-memory v0.1.0")
    print("Exp1 lateral gap (structured - random same count):")
    for name, v in res["exp1_lateral_gap"].items():
        if name == "bar_L1":
            continue
        print(f"  {name}: structured {v['structured_mean']:.3f} "
              f"random {v['random_mean']:.3f} gap {v['gap_mean']:.3f} "
              f"(per seed {v['gap_per_seed']})")
    bar = res["exp1_lateral_gap"]["bar_L1"]
    print(f"  bar L1: mean gap {bar['mean_gap']:.3f}, "
          f"{bar['n_ge_0.10']}/3 >= 0.10, pass = {bar['pass']}")
    g = res["exp2_gate"]
    print(f"Exp2 gate: tau {g['tau']:.3f}, validation J {g['validation_J']:.3f}, "
          f"held-out J {g['held_out']['J']:.3f} "
          f"TPR {g['held_out']['TPR']:.2f} FPR {g['held_out']['FPR']:.2f}, "
          f"pass L2 = {g['pass_L2']}")
    print(f"Exp3 recall (CEILING): {res['exp3_recall_ceiling']}")
    c = res["exp4_controls"]
    print(f"Exp4 controls: random {c['random_pattern_mean']:.3f} "
          f"scrambled {c['scrambled_mean']:.3f}, pass L4 = {c['pass_L4']}")
    with open("results.json", "w") as f:
        json.dump(res, f, indent=2)
    print("wrote results.json")


if __name__ == "__main__":
    main()
