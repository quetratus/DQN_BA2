import os
from random import random, randint, sample
import shutil
import numpy as np
import torch
import torch.nn as nn
import torchvision.utils
from tensorboardX import SummaryWriter
import datetime
import optuna


from deep_q_network import DeepQNetwork
from setup_V2 import DQNAgent, pre_processing
from utils import get_arg_parser

'''
def get_args():

    parser = argparse.ArgumentParser("""Implementation of Deep Q Network""")
    parser.add_argument("--image_size", type=int, default=84, help="The common width and height for all images")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size for replay memory")
    parser.add_argument("--optimizer", type=str, choices=["sgd", "adam"], default="adam")
    parser.add_argument("--lr", type=float, default=1e-6, help="learning rate for optimizer")
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

    args = parser.parse_args()

    return args
'''


def get_args():
    parser = get_arg_parser()
    args = parser.parse_args()
    return args


def train(opt):
    if torch.cuda.is_available():
        torch.cuda.manual_seed(123)
    else:
        torch.manual_seed(123)
    model = DeepQNetwork()
    if os.path.isdir(opt.log_path):
        # remove dir if it already exists
        shutil.rmtree(opt.log_path)
    os.makedirs(opt.log_path)
 #   writer = SummaryWriter(opt.log_path)
    writer = SummaryWriter()

    optimizer = torch.optim.Adam(model.parameters(), lr=opt.lr)
    criterion = nn.MSELoss()
    game_state = DQNAgent()
    state, reward, done = game_state.step(0)
    state = pre_processing(state[:game_state.screen_width, :int(game_state.screen_height)], opt.image_size, opt.image_size)
    state = torch.from_numpy(state)
    if torch.cuda.is_available():
        model.cuda()
        state = state.cuda()
    state_image = torch.cat(tuple(state for _ in range(4)))[None, :, :, :]

    replay_memory = []
    iter = 0
    while iter < opt.num_iters:
        prediction = model(state_image)[0]
        # Exploration or exploitation
        epsilon = opt.final_epsilon + (
                (opt.num_iters - iter) * (opt.initial_epsilon - opt.final_epsilon) / opt.num_iters)
        u = random()
        random_action = u <= epsilon
        if random_action:
            print("Perform a random action")
            action = randint(0, 2)
        else:

            action = torch.argmax(prediction).item()

        next_state, reward, done = game_state.step(action)
        next_state = pre_processing(next_state[:game_state.screen_width, :int(game_state.screen_height)], opt.image_size,
                                    opt.image_size)
        next_state = torch.from_numpy(next_state)
        if torch.cuda.is_available():
            next_state = next_state.cuda()
        next_state_image = torch.cat((state_image[0, 1:, :, :], next_state))[None, :, :, :]
        replay_memory.append([state_image, action, reward, next_state_image, done])
        if len(replay_memory) > opt.replay_memory_size:
            del replay_memory[0]
        batch = sample(replay_memory, min(len(replay_memory), opt.batch_size))
        state_batch, action_batch, reward_batch, next_state_batch, terminal_batch = zip(*batch)

        state_batch = torch.cat(tuple(state_image for state_image in state_batch))
        action_batch = torch.from_numpy(
            np.array([[1, 0, 0] if action == 0 else [0, 1, 0] if action == 1 else [0, 0, 1] for action in
                      action_batch], dtype=np.float32))
        reward_batch = torch.from_numpy(np.array(reward_batch, dtype=np.float32)[:, None])
        next_state_batch = torch.cat(tuple(state_image for state_image in next_state_batch))

        if torch.cuda.is_available():
            state_batch = state_batch.cuda()
            action_batch = action_batch.cuda()
            reward_batch = reward_batch.cuda()
            next_state_batch = next_state_batch.cuda()
        current_prediction_batch = model(state_batch)
        next_prediction_batch = model(next_state_batch)

        y_batch = torch.cat(
            tuple(reward if terminal else reward + opt.gamma * torch.max(prediction) for reward, terminal, prediction in
                  zip(reward_batch, terminal_batch, next_prediction_batch)))

        q_value = torch.sum(current_prediction_batch * action_batch, dim=1)
        optimizer.zero_grad()
        loss = criterion(q_value, y_batch)
        loss.backward()
        optimizer.step()

        state_image = next_state_image
        iter += 1


        print("Iteration: {}/{}, Action: {}, Loss: {:.5f}, Epsilon {:.5f}, Reward: {}, Q-value: {}".format(
            iter + 1,
            opt.num_iters,
            action,
            loss,
            epsilon,
            reward,
            torch.max(prediction)))
     #   writer.add_scalar('Train/Loss', loss, iter)
      #  writer.add_scalar('Train/Epsilon', epsilon, iter)
       # writer.add_scalar('Train/Reward', reward, iter)
       # writer.add_scalar('Train/Q-value', torch.max(prediction), iter)
       # writer.add_image('images', state, 0)
        if (iter+1) % 50000 == 0:
            torch.save(model, "{}/dqn_penguin_{}".format(opt.saved_path, iter+1))
    torch.save(model, "{}/dqn_penguin".format(opt.saved_path))
    writer.close()


if __name__ == "__main__":
    opt = get_args()
    train(opt)

