from characters import *
##############
# AI parameters
##############

def define_parameters():
    params = dict()
    params['epsilon_decay_linear'] = 1 / 75  # epsilon
    params['learning_rate'] = 0.0005
    params['first_layer_size'] = 30  # neurons in the first layer
    params['second_layer_size'] = 30  # neurons in the second layer
    params['third_layer_size'] = 30  # neurons in the third layer
    params['episodes'] = 30  # number of episodes to train the AI agent
    params['memory_size'] = 250  # memory size
    params['batch_size'] = 32  # batch size
    params['weights_path'] = 'weights/weights.hdf5'  # define the weights and save them to file
    params['load_weights'] = False
    params['train'] = True
    return params


# Initialise with parameters
def init_state1(penguin, game, enemy, agent, batch_size):
    # this represent an array of the type  [0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0]
    state_init1 = agent.get_state(game, penguin, enemy)
    action = [1, 0, 0]  # run, jump, duck
    penguin.do_move(action, penguin.x, penguin.y, game, enemy, agent)
    state_init2 = agent.get_state(game, penguin, enemy)

    # reward function
    reward1 = agent.set_reward(penguin, game.crash)
    agent.remember(state_init1, action, reward1, state_init2, game.crash)
    agent.replay_new(agent.memory, batch_size)

