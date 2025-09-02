import logging
import time
from contextlib import contextmanager
from enum import Enum
from typing import Generator, List, Optional, Callable, Type, Union

from sqlalchemy import create_engine, Column, Integer, String, text, inspect
from sqlalchemy.exc import OperationalError, DatabaseError, PendingRollbackError
from sqlalchemy.orm import declarative_base, sessionmaker, Session, scoped_session, UOWTransaction, DeclarativeMeta
from sqlalchemy import event


class Trigger:
    def __init__(self, name: str):
        self.name = name

    def __call__(self, *args, **kwargs):
        ...


class TriggerBeforeFlushEnum(Enum):
    NEW = "new"
    DELETED = "deleted"
    DIRTY = "dirty"

    def apply(self, session):
        if self is TriggerBeforeFlushEnum.NEW:
            return session.new
        if self is TriggerBeforeFlushEnum.DELETED:
            return session.deleted
        if self is TriggerBeforeFlushEnum.DIRTY:
            return session.dirty


class TriggerBeforeFlush(Trigger):
    class _TriggerBeforeFlushData:
        def __init__(
                self,
                lamda: Callable[[Session, object], None],
                models: List[Type[DeclarativeMeta]],
                types: List[TriggerBeforeFlushEnum],
                columns: List[str],
                once: bool
        ):
            self.lamda = lamda
            self.models = models
            self.types = types
            self.columns = columns
            self.once = once
            self._called = False

        def run(self, session: Session, instance: object):
            if self._called and self.once:
                return
            self._called = True
            self.lamda(session, instance)

        def is_yes(self, session: Session, instance: object, type: TriggerBeforeFlushEnum, name_attr: str, attr):
            if self.models:
                for model in self.models:
                    if instance.__class__ == model:
                        break
                else:
                    return

            if self.types:
                for type_valid in self.types:
                    if type_valid == type:
                        break
                else:
                    return

            if self.columns:
                for column_valid in self.columns:
                    if column_valid == name_attr:
                        break
                else:
                    return

            self.run(session, instance)

    def __init__(self):
        super().__init__("before_flush")
        self._triggers: List[TriggerBeforeFlush._TriggerBeforeFlushData] = []

    def add_before_flush(
            self,
            lamda: Callable[[Session, object], None],
            models: Optional[Union[Type[DeclarativeMeta], List[Type[DeclarativeMeta]]]] = None,
            types: Optional[Union[TriggerBeforeFlushEnum, List[TriggerBeforeFlushEnum]]] = None,
            columns: Optional[Union[str, List[str]]] = None,
            once: bool = False
    ):
        if models is None:
            models = []
        elif not isinstance(models, (list, tuple)):
            models = [models]

        if types is None:
            types = []
        elif not isinstance(types, (list, tuple)):
            types = [types]

        if columns is None:
            columns = []
        elif isinstance(columns, str):
            columns = [columns]

        self._triggers.append(TriggerBeforeFlush._TriggerBeforeFlushData(
            lamda=lamda,
            models=models,
            types=types,
            columns=columns,
            once=once,
        ))

    def __call__(self, session: Session, flush_context: UOWTransaction, instances):
        if len(self._triggers) == 0:
            pass
        for enum in TriggerBeforeFlushEnum:
            objs = enum.apply(session)
            for obj in objs:
                state = inspect(obj)
                for name_attr, attr in state.attrs.items():
                    if attr.history.has_changes():
                        for trigger in self._triggers:
                            trigger.is_yes(session, obj, enum, name_attr, attr)


class DB:
    def __init__(self, url, **kwargs):
        self.engine = create_engine(url, **kwargs)
        self.Base = declarative_base()
        self.SessionLocal = scoped_session(sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        ))

    def drop_all(self):
        self.Base.metadata.drop_all(bind=self.engine)

    def create_all(self):
        self.Base.metadata.create_all(bind=self.engine)

    def get_db(self) -> Generator[Session, None, None]:
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @property
    def Model(self):
        return self.Base

    @contextmanager
    def get_db_session(self, retries=5, delay=5, triggers: List[Trigger] = None) -> Generator[Session, None, None]:
        session = None
        if triggers is None:
            triggers = []
        for attempt in range(retries):
            try:
                session = self.SessionLocal()
                # Проверяем соединение
                session.execute(text("SELECT 1"))
                break
            except PendingRollbackError as e:
                session.rollback()
                time.sleep(delay)
            except OperationalError as e:
                logging.warning(f"[{attempt + 1}/{retries}] Потеря соединения с БД: {e}")
                time.sleep(delay)
            except DatabaseError as e:
                logging.warning(f"[{attempt + 1}/{retries}] Потеря соединения с БД: {e}")
                time.sleep(delay)
        if session is None:
            raise e
        try:
            for trigger in triggers:
                event.listen(session, trigger.name, trigger)

            yield session
        except:
            session.rollback()
            raise
        finally:
            for trigger in triggers:
                event.remove(session, trigger.name, trigger)
            session.close()
            # self.SessionLocal.remove()
