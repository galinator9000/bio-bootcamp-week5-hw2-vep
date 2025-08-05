from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func
import os

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/vep_homework")
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Gene(Base):
    __tablename__ = 'gene'
    gene_id = Column(Integer, primary_key=True)

    symbol = Column(String, unique=True, nullable=False)
    biotype = Column(String)

    # Define a one-to-many relationship with variants
    variants = relationship("Variant", back_populates="gene")

class Variant(Base):
    __tablename__ = 'variant'
    variant_id = Column(Integer, primary_key=True)
    
    chrom = Column(String, nullable=False)
    pos = Column(Integer, nullable=False)
    ref = Column(String)
    alt = Column(String)
    rs_id = Column(String, nullable=True)
    impact = Column(String)

    # Gene relation
    gene_id = Column(Integer, ForeignKey('gene.gene_id'))
    gene = relationship("Gene", back_populates="variants")

    # One-to-many relationship with variant calls
    calls = relationship("VariantCall", back_populates="variant")

class VariantCall(Base):
    __tablename__ = 'variant_call'
    vc_id = Column(Integer, primary_key=True)

    # The INFO fields from the VCF file can be complex,
    # so we'll store a few key ones.
    sample_name = Column(String)
    genotype = Column(String)
    depth = Column(String)

    # Relation to the Variant table
    variant_id = Column(Integer, ForeignKey('variant.variant_id'))
    variant = relationship("Variant", back_populates="calls")

def create_tables():
    print("Creating database tables...")
    Base.metadata.create_all(engine)
    print("Tables created successfully.")