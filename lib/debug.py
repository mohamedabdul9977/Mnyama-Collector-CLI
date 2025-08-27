"""
Debug utilities for the Mnyama Collector CLI
"""

from models import get_session, Species, Creature, Habitat
from helpers import print_header

def seed_sample_data():
    """Add sample data for testing"""
    session = get_session()
    
    try:
        print_header("Seeding Sample Data")
        
        # Create sample species
        if not session.query(Species).filter_by(name="African Lion").first():
            lion = Species(
                name="African Lion",
                diet_type="Carnivore",
                natural_habitat="Savanna",
                size=50,
                threat_status="Vulnerable"
            )
            session.add(lion)
        
        if not session.query(Species).filter_by(name="Emperor Penguin").first():
            penguin = Species(
                name="Emperor Penguin",
                diet_type="Carnivore",
                natural_habitat="Antarctica",
                size=5,
                threat_status="Stable"
            )
            session.add(penguin)
        
        if not session.query(Species).filter_by(name="Giant Panda").first():
            panda = Species(
                name="Giant Panda",
                diet_type="Herbivore",
                natural_habitat="Bamboo Forest",
                size=40,
                threat_status="Endangered"
            )
            session.add(panda)
        
        session.commit()
        
        # Get species for creating creatures
        lion = session.query(Species).filter_by(name="African Lion").first()
        penguin = session.query(Species).filter_by(name="Emperor Penguin").first()
        panda = session.query(Species).filter_by(name="Giant Panda").first()
        
        # Create sample creatures
        creatures_data = [
            ("Simba", 5, lion),
            ("Nala", 4, lion),
            ("Mumble", 2, penguin),
            ("Gloria", 3, penguin),
            ("Po", 6, panda),
            ("Mei Mei", 4, panda)
        ]
        
        for name, age, species in creatures_data:
            if not session.query(Creature).filter_by(name=name).first():
                creature = Creature(name=name, age=age, species_id=species.id)
                session.add(creature)
        
        session.commit()
        
        # Create sample habitats
        habitats_data = [
            ("Big Cats Enclosure", "Grassland", 200),
            ("Penguin Paradise", "Arctic", 150),
            ("Bamboo Grove", "Forest", 180),
            ("Mixed Herbivore Sanctuary", "Forest", 300)
        ]
        
        for name, biome, footage in habitats_data:
            if not session.query(Habitat).filter_by(name=name).first():
                habitat = Habitat(name=name, biome_type=biome, square_footage=footage)
                session.add(habitat)
        
        session.commit()
        
        print("✅ Sample data seeded successfully!")
        print("Sample data includes:")
        print("  • 3 Species (Lion, Penguin, Panda)")
        print("  • 6 Creatures (2 of each species)")  
        print("  • 4 Habitats with different biomes")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        session.rollback()
    finally:
        session.close()

def show_database_stats():
    """Show current database statistics"""
    session = get_session()
    
    try:
        print_header("Database Statistics")
        
        species_count = session.query(Species).count()
        creature_count = session.query(Creature).count()
        habitat_count = session.query(Habitat).count()
        
        print(f"Species: {species_count}")
        print(f"Creatures: {creature_count}")
        print(f"Habitats: {habitat_count}")
        
        # Show creatures per species
        print("\nCreatures per Species:")
        species_list = session.query(Species).all()
        for species in species_list:
            count = len(species.creatures)
            print(f"  • {species.name}: {count} individuals")
        
        # Show habitat occupancy
        print("\nHabitat Occupancy:")
        habitat_list = session.query(Habitat).all()
        for habitat in habitat_list:
            count = len(habitat.creatures)
            capacity = f"{habitat.current_capacity}/{habitat.square_footage} sq ft"
            print(f"  • {habitat.name}: {count} creatures ({capacity})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        session.close()

def clear_all_data():
    """Clear all data from database (for testing)"""
    session = get_session()
    
    try:
        confirm = input("⚠️  This will delete ALL data. Are you sure? (type 'DELETE' to confirm): ")
        if confirm != 'DELETE':
            print("Operation cancelled.")
            return
        
        # Delete all records
        session.query(Creature).delete()
        session.query(Habitat).delete()
        session.query(Species).delete()
        session.commit()
        
        print("✅ All data cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        session.rollback()
    finally:
        session.close()

def main():
    """Debug menu"""
    while True:
        print_header("Debug Menu")
        print("1. Seed sample data")
        print("2. Show database statistics")
        print("3. Clear all data")
        print("4. Exit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            seed_sample_data()
        elif choice == "2":
            show_database_stats()
        elif choice == "3":
            clear_all_data()
        elif choice == "4":
            break
        else:
            print("Invalid choice!")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()