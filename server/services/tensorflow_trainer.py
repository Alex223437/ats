# services/tensorflow_trainer.py
from ai_model.trainers.train_conservative import train_classifier

def train_model_for_strategy(strategy, user_id):
    if not strategy.training_ticker or not strategy.training_from_date or not strategy.training_to_date:
        raise ValueError("Missing training parameters in strategy")

    train_classifier(
        ticker=strategy.training_ticker,
        user_id=user_id,
        from_date=strategy.training_from_date,
        to_date=strategy.training_to_date
    )