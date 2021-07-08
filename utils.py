import argparse


def get_arg_parser():

    parser = argparse.ArgumentParser("""Implementation of Deep Q Network""")
    parser.add_argument("--image_size", type=int, default=84, help="The common width and height for all images")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size for replay memory")
    parser.add_argument("--optimizer", type=str, choices=["sgd", "adam"], default="adam")
    parser.add_argument("--lr", type=float, default=1e-4, help="learning rate for optimizer")
    parser.add_argument("--gamma", type=float, default=0.99, help="discount factor for future rewards")
    parser.add_argument("--initial_epsilon", type=float, default=0.1,
                        help="initial value of epsilon in epsilon-greedy action selection")
    parser.add_argument("--final_epsilon", type=float, default=1e-4,
                        help="final value of epsilon in epsilon-greedy action selection")
    parser.add_argument("--num_iters", type=int, default=200000)
    parser.add_argument("--replay_memory_size", type=int, default=50000,
                        help="Number of epochs between testing phases")
   # parser.add_argument("--log_path", type=str, default="tensorboard")
    parser.add_argument("--log_path", type=str, default="tensorboard/exp2")

   # parser.add_argument("--saved_path", type=str, default="trained_models")
    parser.add_argument("--saved_path", type=str, default="trained_models")

  #  args = parser.parse_args()

    return parser