import argparse
import torch

from setup_V2 import DQNAgent, pre_processing


def get_args():
    parser = argparse.ArgumentParser("""Implementation of Deep Q Network""")
    parser.add_argument("--image_size", type=int, default=84, help="The common width and height for all images")
 #   parser.add_argument("--saved_path", type=str, default="trained_models")
    parser.add_argument("--saved_path", type=str, default="trained_models")


    args = parser.parse_args()
    return args


def test(opt):
    if torch.cuda.is_available():
        torch.cuda.manual_seed(123)
    else:
        torch.manual_seed(123)
    if torch.cuda.is_available():
        model = torch.load("{}/dqn_penguin".format(opt.saved_path))
    else:
        model = torch.load("{}/dqn_penguin".format(opt.saved_path), map_location=lambda storage, loc: storage)
    model.eval()
    game_state = DQNAgent()
    state, reward, done = game_state.step(0)
    state = pre_processing(state[:game_state.screen_width, :int(game_state.screen_height)], opt.image_size, opt.image_size)
    state = torch.from_numpy(state)
    if torch.cuda.is_available():
        model.cuda()
        state = state.cuda()
    state_image = torch.cat(tuple(state for _ in range(4)))[None, :, :, :]

    while True:
        prediction = model(state_image)[0]
        action = torch.argmax(prediction).item()

        next_image, reward, done = game_state.step(action)
        next_image = pre_processing(next_image[:game_state.screen_width, :int(game_state.screen_height)], opt.image_size,
                                    opt.image_size)
        next_image = torch.from_numpy(next_image)
        if torch.cuda.is_available():
            next_image = next_image.cuda()
        next_state_image = torch.cat((state_image[0, 1:, :, :], next_image))[None, :, :, :]

        state_image = next_state_image


if __name__ == "__main__":
    opt = get_args()
    test(opt)