from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from . import Base
from datetime import datetime

# Association table for many-to-many relationship between Creature and Habitat
creature_habitats = Table(
    'creature_habitats',
    Base.metadata,
    Column('creature_id', Integer, ForeignKey('creatures.id'), primary_key=True),
    Column('habitat_id', Integer, ForeignKey('habitats.id'), primary_key=True)
)

class Species(Base):
    __tablename__ = 'species'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    _diet_type = Column('diet_type', String, nullable=False)
    natural_habitat = Column(String)
    size = Column(Integer, default=10)  # Size in square feet per creature
    threat_status = Column(String, default="Stable")  # Stable, Vulnerable, Endangered
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    creatures = relationship("Creature", back_populates="species")
    
    @hybrid_property
    def diet_type(self):
        return self._diet_type
    
    @diet_type.setter
    def diet_type(self, value):
        valid_diets = ["Carnivore", "Herbivore", "Omnivore"]
        if value not in valid_diets:
            raise ValueError(f"Diet type must be one of: {', '.join(valid_diets)}")
        self._diet_type = value
    
    @validates('_diet_type')
    def validate_diet_type(self, key, diet_type):
        valid_diets = ["Carnivore", "Herbivore", "Omnivore"]
        if diet_type not in valid_diets:
            raise ValueError(f"Diet type must be one of: {', '.join(valid_diets)}")
        return diet_type
    
    def __repr__(self):
        return f"<Species(name='{self.name}', diet='{self.diet_type}', threat_status='{self.threat_status}')>"

class Creature(Base):
    __tablename__ = 'creatures'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    species_id = Column(Integer, ForeignKey('species.id'), nullable=False)
    image_path = Column(String)  # Path to generated image
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    species = relationship("Species", back_populates="creatures")
    habitats = relationship("Habitat", secondary=creature_habitats, back_populates="creatures")
    
    @property
    def size(self):
        """Get size from species"""
        return self.species.size if self.species else 10
    
    def can_coexist_with(self, other_creature):
        """Check if this creature can coexist with another creature"""
        if not other_creature or not other_creature.species:
            return True
            
        # Carnivores generally can't coexist with herbivores (prey relationship)
        if (self.species.diet_type == "Carnivore" and other_creature.species.diet_type == "Herbivore") or \
           (self.species.diet_type == "Herbivore" and other_creature.species.diet_type == "Carnivore"):
            return False
            
        return True
    
    def __repr__(self):
        return f"<Creature(name='{self.name}', species='{self.species.name if self.species else 'Unknown'}', age={self.age})>"

class Habitat(Base):
    __tablename__ = 'habitats'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    biome_type = Column(String, nullable=False)
    square_footage = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    creatures = relationship("Creature", secondary=creature_habitats, back_populates="habitats")
    
    @hybrid_property
    def current_capacity(self):
        """Calculate current space used by all creatures"""
        return sum(creature.size for creature in self.creatures)
    
    @hybrid_property
    def is_full(self):
        """Check if habitat is at or over capacity"""
        return self.current_capacity >= self.square_footage
    
    @property
    def capacity_percentage(self):
        """Get capacity as percentage"""
        if self.square_footage == 0:
            return 100
        return min(100, (self.current_capacity / self.square_footage) * 100)
    
    def can_add_creature(self, creature):
        """Check if a creature can be added to this habitat"""
        # Check capacity
        if self.current_capacity + creature.size > self.square_footage:
            return False, "Habitat would exceed capacity"
        
        # Check coexistence with existing creatures
        for existing_creature in self.creatures:
            if not creature.can_coexist_with(existing_creature):
                return False, f"Cannot coexist with {existing_creature.name} ({existing_creature.species.diet_type})"
        
        return True, "OK"
    
    def add_creature(self, creature):
        """Add a creature to habitat with validation"""
        can_add, reason = self.can_add_creature(creature)
        if not can_add:
            raise ValueError(f"Cannot add {creature.name} to {self.name}: {reason}")
        
        if creature not in self.creatures:
            self.creatures.append(creature)
        
        return True
    
    def __repr__(self):
        return f"<Habitat(name='{self.name}', biome='{self.biome_type}', capacity={self.current_capacity}/{self.square_footage})>"