'''
try:
    import optuna
except ImportError:
    raise RuntimeError("This script requires optuna installed.")

import shutil
from argparse import ArgumentParser
from trainV2 import get_args, train


def dqn_parser_hook(parser: ArgumentParser, trial: optuna.Trial):
    parser.set_defaults(
    batch_size = trial.suggest_categorical("batch_size", [8, 16, 32, 64, 128]),
    lr = trial.suggest_categorical("lr", [1e-6, 1e-5, 1e-4]),
    initial_epsilon = trial.suggest_categorical("initial_epsilon",[0.1, 0.25]),
    final_epsilon = trial.suggest_categorical("final_epsilon",[1e-4, 1e-6]),
    replay_memory_size = trial.suggest_int("replay_memory_size",5000, 50000),
    optimizer = trial.suggest_categorical("optimizer", ["adam", "sgd"]),
    gamma = trial.suggest_categorical("gamma", [0.9, 0.95, 0.98, 0.99, 0.995, 0.999, 0.9999]),
    )
    return parser


def objective(trial: optuna.Trial) -> float:
    args = dqn_parser_hook(ArgumentParser,trial)
    reward = train(args)
    print(trial.params, reward)
    return reward


def optimize_dqn(trials: int) -> optuna.Study:
    study = optuna.create_study(
        storage="sqlite:///dqn.db",
        study_name="dqn1",
        direction="maximize",
        load_if_exists=True,
    )
    study.optimize(objective, n_trials=trials)
    return study


def dump_best_study(study):
    trial = study.best_trial
    print("  Best Value: ", trial.value)
    print("  Best Params: ")
    for key, value in trial.params.items():
        print("    {}: {}".format(key, value))


def main():
    trials = 2

    dqn_study = optimize_dqn(trials)
    dump_best_study(dqn_study)


if __name__ == "__main__":
    main()



def main():
    # Create a new Optuna study object.
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=3, timeout=600)

    print("Study statistics: ")
    print("  Number of finished trials: ", len(study.trials))

    print("Best trial:")
    trial = study.best_trial

    print("  Value: ", trial.value)

    print("  Params: ")
    for key, value in trial.params.items():
        print("    {}: {}".format(key, value))


if __name__ == "__main__":
    main()
    
'''

