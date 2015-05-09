# All database table specifications
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Represents the users
class User(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	number = Column(String)

	def __repr__(self):
		return "<User(ID = %s, Name = %s, Number = %s)>" % (self.id, self.name, self.number)

# Represents the jobs
class Job(Base):
	__tablename__ = 'jobs'

	id = Column(Integer, primary_key=True)
	what = Column(String, nullable=True)
	owner = Column(String)
	issueDate = Column(DateTime, default=func.now())
	deadline = Column(DateTime)
	fromTown = Column(String)
	toTown = Column(String)

	# 0 = Issued, 1 = Accepted, 2 = Expired, 3 = Completed
	status = Column(Integer, default=0)
	accepter = Column(String, nullable=True)
	endDate = Column(DateTime, nullable=True)

	def __repr__(self):
		return "<Job(ID = %d, What = %s, Owner = %s, Issue Date = %s, Deadline = %s, "\
		"From Town = %s, To Town = %s, Status = %d, Accepter = %s, End Date = %s)>" \
		% (self.id, self.what, self.owner, self.issueDate, self.deadline, self.fromTown,\
		self.toTown, self.status, self.accepter, self.endDate)