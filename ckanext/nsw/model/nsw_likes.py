from sqlalchemy import (
    UnicodeText,
    ForeignKey,
    Column,
    Boolean,
    DateTime
)
import datetime
from ckanext.nsw.model.model import Base


class EntityLikes(Base):
    __tablename__ = 'entity_likes'

    id = Column(UnicodeText, primary_key=True)
    user = Column(UnicodeText)
    entity_id = Column(UnicodeText)
    entity_name = Column(UnicodeText)
    entity_type = Column(UnicodeText)
    created = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<EntityLikes: id={0}, user={1}, entity_id={2}, entity_name={3}, entity_type={4}, created={5}>'.format(
            self.id, self.user, self.entity_id, self.entity_name, self.entity_type, self.created 
        )