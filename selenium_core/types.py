from typing import Callable, TypeVar


T_EC = TypeVar('T_EC')
ExpectedConditionPredicate = Callable[..., T_EC]
ExpectedCondition = Callable[..., ExpectedConditionPredicate]
