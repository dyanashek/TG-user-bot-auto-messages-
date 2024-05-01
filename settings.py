import text


from typing import List, Dict, Union, Optional


class AwaitTime:
    MINUTES_PER_HOUR: int = 60
    MINUTES_PER_DAY: int = 1440

    def __init__(self, period: Union[int, float], measure: str) -> None:
        if not isinstance(period, (int, float)):
            raise TypeError("Аргумент 'period' должен быть числом (int или float).")

        if measure == 'minutes':
            multiplier = 1
        elif measure == 'hours':
            multiplier = self.MINUTES_PER_HOUR
        elif measure == 'days':
            multiplier = self.MINUTES_PER_DAY
        else:
            raise ValueError("Недопустимое значение для параметра 'measure'. Допустимые значения: 'minutes', 'hours', 'days'.")

        self.minutes = multiplier * period


class Stage:
    def __init__(self, message: str, await_time: AwaitTime, stage_num: int, triggers: List[Optional[str]] = []) -> None:
        self.message = message
        self.await_time = await_time.minutes
        self.triggers = triggers
        self.stage_num = stage_num


STAGES: Dict[int, Stage] = {
    1 : Stage(text.msg_1, AwaitTime(6, 'minutes'), 1),
    2 : Stage(text.msg_2, AwaitTime(39, 'minutes'), 2, ['триггер1']),
    3 : Stage(text.msg_3, AwaitTime(26, 'hours'), 3),
}

STOP_WORDS: List[str] = ['прекрасно', 'ожидать',]

ALIVE: str = 'alive'
DEAD: str = 'dead'
FINISHED: str = 'finished'