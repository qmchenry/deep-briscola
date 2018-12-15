from hyperopt import hp, tpe, fmin, space_eval
import tensorflow as tf

from agents.deep_agent import DeepAgent
from agents_base.random_agent import RandomAgent
import environment as brisc
import train


space = {
    'discount': hp.uniform('discount', 0.65, 1.0),
    'epsilon': hp.choice('epsilon', [0, 0.5, 0.75]),
    'epsilon_increment' : hp.choice('epsilon_increment', [1e-8, 1e-7, 5e-6, 1e-6, 1e-5]),
    'epsilon_max' : hp.choice('epsilon_max', [0.8, 0.85, 0.9, 0.95, 0.99]),
    'learning_rate' : hp.choice('learning_rate', [1e-5, 1e-4, 1e-3])
}

NUM_EPOCHS=50 * 1000
EVALUATE_EVERY=10 * 1000
EVALUATE_FOR=1000
OUTPUT_DIR='hyperopt_best_model'

def train_agent(hype_space):

    print("----------------------")
    print("Evaluating model: ", hype_space)

    game = brisc.BriscolaGame(2,verbosity=brisc.LoggerLevels.TRAIN)
    tf.reset_default_graph()

    # Initialize agents
    agents = []
    agent = DeepAgent(hype_space['epsilon'], hype_space['epsilon_increment'], hype_space['epsilon_max'], hype_space['discount'])
    agents.append(agent)
    agent = RandomAgent()
    agents.append(agent)

    best_winning_ratio = -1
    for epoch in range(1, NUM_EPOCHS + 1):
        print ("Epoch: ", epoch, end='\r')

        game.reset()
        game_winner_id, winner_points = train.play_episode(game, agents)

        if epoch % EVALUATE_EVERY == 0:
            winning_ratios, _ = train.evaluate(game, agents, EVALUATE_FOR)
            if winning_ratios[0] > best_winning_ratio:
                best_winning_ratio = winning_ratios[0]
                agents[0].save_model(OUTPUT_DIR)

    print ("Best winning ratio ----->", best_winning_ratio)
    min_losing_ratio = 100 - best_winning_ratio
    return min_losing_ratio



if __name__ == "__main__":

    # returns list of indices of parameter choices
    best_model = fmin(
        train_agent,
        space,
        algo=tpe.suggest,
        max_evals=250
    )

    print(best_model)
    print ("Best model is:")
    print(space_eval(space, best_model))