from abc import ABC, abstractmethod
import logging

###

L = logging.getLogger(__name__)


###


class PubSub(ABC):
	def __init__(self):
		super().__init__()

	@abstractmethod
	def init_connection(self):
		L.error("subclasses must override init_connection()!")
		raise NotImplementedError("subclasses must override init_connection()!")

	@abstractmethod
	def close_connection(self):
		L.error("subclasses must override close_connection()!")
		raise NotImplementedError("subclasses must override close_connection()!")

	@abstractmethod
	def register_subscriber(self):
		L.error("subclasses must override register_subscriber()!")
		raise NotImplementedError("subclasses must override register_subscriber()!")

	@abstractmethod
	def publish_data(self):
		L.error("subclasses must override publish_data()!")
		raise NotImplementedError("subclasses must override publish_data()!")

