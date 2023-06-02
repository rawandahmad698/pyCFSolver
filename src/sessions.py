import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import uuid1

from selenium.webdriver.chrome.webdriver import WebDriver

import utils
from dtos import V1RequestBase


@dataclass
class Session:
    session_id: str
    driver: WebDriver
    created_at: datetime

    def lifetime(self) -> timedelta:
        return datetime.now() - self.created_at


class SessionsStorage:
    """SessionsStorage creates, stores and process all the sessions"""

    def __init__(self):
        # Self.sessions is a set of dictionaries with the following structure:
        self.sessions = {}
        self.drivers = {}
        self.real_sessions = []
        self.is_being_created = []

    def create(self, req: V1RequestBase = None, session_id: Optional[str] = None, force_new: Optional[bool] = False) -> Tuple[Session, bool]:
        """create creates new instance of WebDriver if necessary,
        assign defined (or newly generated) session_id to the instance
        and returns the session object. If a new session has been created
        second argument is set to True.

        Note: The function is idempotent, so in case if session_id
        already exists in the storage a new instance of WebDriver won't be created
        and existing session will be returned. Second argument defines if
        new session has been created (True) or an existing one was used (False).
        """
        session_id = session_id or str(uuid1())

        if force_new:
            self.destroy(session_id)

        if self.exists(session_id):
            return self.sessions[session_id], False

        # Try to add it to the real sessions
        if session_id not in self.real_sessions:
            self.real_sessions.append(session_id)
            self.is_being_created.append(session_id)
        else:
            if session_id in self.is_being_created:
                # Wait for it to be created
                while session_id in self.is_being_created:
                    pass

            if session_id in self.sessions:
                return self.sessions[session_id], False
            else:
                self.is_being_created.append(session_id)

        if req is not None:
            driver = utils.get_webdriver(req)
        else:
            driver = utils.get_webdriver()

        created_at = datetime.now()
        session = Session(session_id, driver, created_at)

        self.sessions[session_id] = session
        self.drivers[session_id] = driver

        self.is_being_created.remove(session_id)

        return session, True

    def exists(self, session_id: str) -> bool:
        return session_id in self.sessions

    def destroy(self, session_id: str) -> bool:
        """destroy closes the driver instance and removes session from the storage.
        The function is noop if session_id doesn't exist.
        The function returns True if session was found and destroyed,
        and False if session_id wasn't found.
        """
        if not self.exists(session_id):
            return False

        self.sessions.pop(session_id)

        # Check if session_id is in the drivers dict
        if session_id in self.drivers:
            driver = self.drivers.pop(session_id)
            driver.quit()
            del driver

        if session_id in self.real_sessions:
            self.real_sessions.remove(session_id)

        return True

    def get(self, session_id: str, ttl: Optional[timedelta] = None, req: V1RequestBase = None) -> Tuple[Session, bool]:
        session, fresh = self.create(session_id=session_id)

        if ttl is not None and not fresh and session.lifetime() > ttl:
            # logging.debug(session\'s lifetime has expired, so the session is recreated (session_id={session_id})')
            logging.info(f'Session\'s lifetime has expired, so the session is being recreated (session_id={session_id})')
            session, fresh = self.create(req=req, session_id=session_id, force_new=True)

        return session, fresh

    def session_ids(self) -> list[str]:
        return list(self.sessions.keys())
