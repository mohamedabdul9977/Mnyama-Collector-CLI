import os
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from models import get_session, create_tables, Species, Creature, Habitat, creature_habitats
from helpers import (
    ImageGenerator, print_header, print_menu, get_user_choice,
    print_creature_details, print_habitat_report, format_capacity_bar
)

class CreatureCollectorCLI:
    def __init__(self):
        self.session = get_session()
        self.image_generator = ImageGenerator()
        create_tables()
    
    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()
    
    def run(self):
        """Main CLI loop"""
        print_header("🦁 Mnyama Collector CLI 🐧")
        print("Welcome to the Wildlife Management System!")
        
        while True:
            try:
                self.show_main_menu()
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\nError: {e}")
                print("Please try again.")
    
    def show_main_menu(self):
        """Display main menu and handle user choice"""
        options = [
            "Manage Species",
            "Manage Creatures", 
            "Manage Habitats",
            "View Habitat Reports",
            "Exit"
        ]
        
        print_menu("Main Menu", options[:-1])
        print(f"{len(options)}. Exit")
        
        choice = get_user_choice(len(options))
        
        if choice == 1:
            self.manage_species()
        elif choice == 2:
            self.manage_creatures()
        elif choice == 3:
            self.manage_habitats()
        elif choice == 4:
            self.view_habitat_reports()
        elif choice == 5:
            print("Goodbye! 👋")
            sys.exit(0)
    
    def manage_species(self):
        """Species management submenu"""
        while True:
            options = [
                "Create a new species",
                "View all species",
                "Find species by diet type",
                "Update species",
                "Delete species"
            ]
            
            print_menu("Species Management", options)
            choice = get_user_choice(len(options) + 1)
            
            if choice == 1:
                self.create_species()
            elif choice == 2:
                self.view_all_species()
            elif choice == 3:
                self.find_species_by_diet()
            elif choice == 4:
                self.update_species()
            elif choice == 5:
                self.delete_species()
            elif choice == len(options) + 1:
                break
    
    def create_species(self):
        """Create a new species"""
        print("\n--- Create New Species ---")
        
        try:
            name = input("Species name: ").strip()
            if not name:
                print("Species name cannot be empty!")
                return
            
            # Check if species already exists
            existing = self.session.query(Species).filter_by(name=name).first()
            if existing:
                print(f"Species '{name}' already exists!")
                return
            
            print("\nAvailable diet types:")
            diet_types = ["Carnivore", "Herbivore", "Omnivore"]
            for i, diet in enumerate(diet_types, 1):
                print(f"{i}. {diet}")
            
            diet_choice = get_user_choice(len(diet_types))
            diet_type = diet_types[diet_choice - 1]
            
            natural_habitat = input("Natural habitat: ").strip()
            
            size = input("Size (sq ft per individual, default 10): ").strip()
            size = int(size) if size.isdigit() else 10
            
            threat_status = input("Threat status (Stable/Vulnerable/Endangered, default Stable): ").strip()
            if not threat_status:
                threat_status = "Stable"
            
            # Create species
            species = Species(
                name=name,
                diet_type=diet_type,
                natural_habitat=natural_habitat,
                size=size,
                threat_status=threat_status
            )
            
            self.session.add(species)
            self.session.commit()
            
            print(f"✅ Species '{name}' created successfully!")
            
        except ValueError as e:
            print(f"❌ Error: {e}")
            self.session.rollback()
        except Exception as e:
            print(f"❌ Error creating species: {e}")
            self.session.rollback()
    
    def view_all_species(self):
        """View all species"""
        species_list = self.session.query(Species).all()
        
        if not species_list:
            print("\n📝 No species found.")
            return
        
        print(f"\n📋 All Species ({len(species_list)} total)")
        print("-" * 80)
        
        for species in species_list:
            creature_count = len(species.creatures)
            print(f"• {species.name}")
            print(f"  Diet: {species.diet_type} | Size: {species.size} sq ft | Status: {species.threat_status}")
            print(f"  Habitat: {species.natural_habitat or 'Not specified'} | Individuals: {creature_count}")
            print()
    
    def find_species_by_diet(self):
        """Find species by diet type"""
        print("\nSelect diet type:")
        diet_types = ["Carnivore", "Herbivore", "Omnivore"]
        for i, diet in enumerate(diet_types, 1):
            print(f"{i}. {diet}")
        
        choice = get_user_choice(len(diet_types))
        selected_diet = diet_types[choice - 1]
        
        species_list = self.session.query(Species).filter_by(diet_type=selected_diet).all()
        
        if not species_list:
            print(f"\n📝 No {selected_diet.lower()} species found.")
            return
        
        print(f"\n🍽️  {selected_diet} Species ({len(species_list)} found)")
        print("-" * 60)
        
        for species in species_list:
            creature_count = len(species.creatures)
            print(f"• {species.name} - {creature_count} individuals")
    
    def update_species(self):
        """Update an existing species"""
        species_list = self.session.query(Species).all()
        
        if not species_list:
            print("\n📝 No species found to update.")
            return
        
        print("\nSelect species to update:")
        for i, species in enumerate(species_list, 1):
            print(f"{i}. {species.name}")
        
        choice = get_user_choice(len(species_list))
        species = species_list[choice - 1]
        
        print(f"\nUpdating: {species.name}")
        print("(Press Enter to keep current value)")
        
        # Update fields
        new_name = input(f"Name [{species.name}]: ").strip()
        if new_name:
            species.name = new_name
        
        print(f"\nCurrent diet: {species.diet_type}")
        print("Diet types: 1. Carnivore, 2. Herbivore, 3. Omnivore")
        diet_choice = input("New diet (1-3, or Enter to keep current): ").strip()
        if diet_choice in ['1', '2', '3']:
            diet_types = ["Carnivore", "Herbivore", "Omnivore"]
            species.diet_type = diet_types[int(diet_choice) - 1]
        
        new_habitat = input(f"Natural habitat [{species.natural_habitat}]: ").strip()
        if new_habitat:
            species.natural_habitat = new_habitat
        
        new_size = input(f"Size [{species.size}]: ").strip()
        if new_size and new_size.isdigit():
            species.size = int(new_size)
        
        new_status = input(f"Threat status [{species.threat_status}]: ").strip()
        if new_status:
            species.threat_status = new_status
        
        try:
            self.session.commit()
            print(f"✅ Species '{species.name}' updated successfully!")
        except Exception as e:
            print(f"❌ Error updating species: {e}")
            self.session.rollback()
    
    def delete_species(self):
        """Delete a species"""
        species_list = self.session.query(Species).all()
        
        if not species_list:
            print("\n📝 No species found to delete.")
            return
        
        print("\nSelect species to delete:")
        for i, species in enumerate(species_list, 1):
            creature_count = len(species.creatures)
            print(f"{i}. {species.name} ({creature_count} individuals)")
        
        choice = get_user_choice(len(species_list))
        species = species_list[choice - 1]
        
        if species.creatures:
            print(f"⚠️  Cannot delete '{species.name}' - it has {len(species.creatures)} individuals!")
            print("Please remove or reassign all creatures first.")
            return
        
        confirm = input(f"Are you sure you want to delete '{species.name}'? (y/N): ").lower()
        if confirm != 'y':
            print("Deletion cancelled.")
            return
        
        try:
            self.session.delete(species)
            self.session.commit()
            print(f"✅ Species '{species.name}' deleted successfully!")
        except Exception as e:
            print(f"❌ Error deleting species: {e}")
            self.session.rollback()
    
    def manage_creatures(self):
        """Creature management submenu"""
        while True:
            options = [
                "Create a new creature",
                "View all creatures",
                "Find creature by name",
                "Assign creature to habitat",
                "Remove creature from habitat",
                "Update creature",
                "Delete creature"
            ]
            
            print_menu("Creature Management", options)
            choice = get_user_choice(len(options) + 1)
            
            if choice == 1:
                self.create_creature()
            elif choice == 2:
                self.view_all_creatures()
            elif choice == 3:
                self.find_creature_by_name()
            elif choice == 4:
                self.assign_creature_to_habitat()
            elif choice == 5:
                self.remove_creature_from_habitat()
            elif choice == 6:
                self.update_creature()
            elif choice == 7:
                self.delete_creature()
            elif choice == len(options) + 1:
                break
    
    def create_creature(self):
        """Create a new creature with image generation"""
        print("\n--- Create New Creature ---")
        
        # Get available species
        species_list = self.session.query(Species).all()
        if not species_list:
            print("❌ No species found! Please create a species first.")
            return
        
        try:
            name = input("Creature name: ").strip()
            if not name:
                print("Creature name cannot be empty!")
                return
            
            age = input("Age (years): ").strip()
            age = int(age) if age.isdigit() else 0
            
            print("\nAvailable species:")
            for i, species in enumerate(species_list, 1):
                print(f"{i}. {species.name} ({species.diet_type})")
            
            species_choice = get_user_choice(len(species_list))
            selected_species = species_list[species_choice - 1]
            
            # Create creature
            creature = Creature(
                name=name,
                age=age,
                species_id=selected_species.id
            )
            
            self.session.add(creature)
            self.session.commit()
            
            print(f"✅ Creature '{name}' created successfully!")
            
            # Generate image for the creature
            print("🎨 Generating creature image...")
            image_path, message = self.image_generator.generate_creature_image(name, selected_species.name)
            
            if image_path:
                creature.image_path = image_path
                self.session.commit()
                print(f"🖼️  {message}")
                print(f"📁 Image saved to: {image_path}")
            else:
                print(f"⚠️  Image generation failed: {message}")
            
        except ValueError as e:
            print(f"❌ Error: {e}")
            self.session.rollback()
        except Exception as e:
            print(f"❌ Error creating creature: {e}")
            self.session.rollback()
    
    def view_all_creatures(self):
        """View all creatures"""
        creatures = self.session.query(Creature).all()
        
        if not creatures:
            print("\n📝 No creatures found.")
            return
        
        print(f"\n🦁 All Creatures ({len(creatures)} total)")
        print("-" * 80)
        
        for creature in creatures:
            habitat_names = [h.name for h in creature.habitats] if creature.habitats else ["Unassigned"]
            print(f"• {creature.name} (Age: {creature.age})")
            print(f"  Species: {creature.species.name} ({creature.species.diet_type})")
            print(f"  Habitats: {', '.join(habitat_names)}")
            if creature.image_path:
                print(f"  Image: {creature.image_path}")
            print()
    
    def find_creature_by_name(self):
        """Find and display creature by name"""
        name = input("\nEnter creature name to search: ").strip()
        if not name:
            return
        
        creatures = self.session.query(Creature).filter(Creature.name.ilike(f"%{name}%")).all()
        
        if not creatures:
            print(f"\n📝 No creatures found matching '{name}'.")
            return
        
        print(f"\n🔍 Found {len(creatures)} creature(s) matching '{name}':")
        print("-" * 60)
        
        for creature in creatures:
            print_creature_details(creature)
    
    def assign_creature_to_habitat(self):
        """Assign a creature to a habitat"""
        creatures = self.session.query(Creature).all()
        habitats = self.session.query(Habitat).all()
        
        if not creatures:
            print("\n📝 No creatures found.")
            return
        
        if not habitats:
            print("\n📝 No habitats found. Please create a habitat first.")
            return
        
        print("\nSelect creature:")
        for i, creature in enumerate(creatures, 1):
            current_habitats = [h.name for h in creature.habitats] if creature.habitats else ["None"]
            print(f"{i}. {creature.name} ({creature.species.name}) - Currently in: {', '.join(current_habitats)}")
        
        creature_choice = get_user_choice(len(creatures))
        selected_creature = creatures[creature_choice - 1]
        
        print("\nSelect habitat:")
        for i, habitat in enumerate(habitats, 1):
            capacity_info = format_capacity_bar(habitat.current_capacity, habitat.square_footage, 20)
            print(f"{i}. {habitat.name} ({habitat.biome_type}) - {capacity_info}")
        
        habitat_choice = get_user_choice(len(habitats))
        selected_habitat = habitats[habitat_choice - 1]
        
        try:
            # Check if creature can be added
            can_add, reason = selected_habitat.can_add_creature(selected_creature)
            
            if not can_add:
                print(f"❌ Cannot assign {selected_creature.name} to {selected_habitat.name}: {reason}")
                return
            
            # Add creature to habitat
            if selected_creature not in selected_habitat.creatures:
                selected_habitat.creatures.append(selected_creature)
                self.session.commit()
                print(f"✅ {selected_creature.name} assigned to {selected_habitat.name} successfully!")
            else:
                print(f"ℹ️  {selected_creature.name} is already in {selected_habitat.name}.")
                
        except Exception as e:
            print(f"❌ Error assigning creature: {e}")
            self.session.rollback()
    
    def remove_creature_from_habitat(self):
        """Remove a creature from a habitat"""
        creatures = self.session.query(Creature).filter(Creature.habitats.any()).all()
        
        if not creatures:
            print("\n📝 No creatures are currently assigned to habitats.")
            return
        
        print("\nSelect creature to remove from habitat:")
        for i, creature in enumerate(creatures, 1):
            habitat_names = [h.name for h in creature.habitats]
            print(f"{i}. {creature.name} - In: {', '.join(habitat_names)}")
        
        creature_choice = get_user_choice(len(creatures))
        selected_creature = creatures[creature_choice - 1]
        
        if len(selected_creature.habitats) == 1:
            # Only one habitat, remove from it
            habitat = selected_creature.habitats[0]
            confirm = input(f"Remove {selected_creature.name} from {habitat.name}? (y/N): ")
            if confirm.lower() == 'y':
                try:
                    habitat.creatures.remove(selected_creature)
                    self.session.commit()
                    print(f"✅ {selected_creature.name} removed from {habitat.name}.")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    self.session.rollback()
        else:
            # Multiple habitats, let user choose
            print(f"\nSelect habitat to remove {selected_creature.name} from:")
            for i, habitat in enumerate(selected_creature.habitats, 1):
                print(f"{i}. {habitat.name}")
            
            habitat_choice = get_user_choice(len(selected_creature.habitats))
            selected_habitat = selected_creature.habitats[habitat_choice - 1]
            
            try:
                selected_habitat.creatures.remove(selected_creature)
                self.session.commit()
                print(f"✅ {selected_creature.name} removed from {selected_habitat.name}.")
            except Exception as e:
                print(f"❌ Error: {e}")
                self.session.rollback()
    
    def update_creature(self):
        """Update creature information"""
        creatures = self.session.query(Creature).all()
        
        if not creatures:
            print("\n📝 No creatures found.")
            return
        
        print("\nSelect creature to update:")
        for i, creature in enumerate(creatures, 1):
            print(f"{i}. {creature.name} ({creature.species.name})")
        
        choice = get_user_choice(len(creatures))
        creature = creatures[choice - 1]
        
        print(f"\nUpdating: {creature.name}")
        print("(Press Enter to keep current value)")
        
        new_name = input(f"Name [{creature.name}]: ").strip()
        if new_name:
            creature.name = new_name
        
        new_age = input(f"Age [{creature.age}]: ").strip()
        if new_age and new_age.isdigit():
            creature.age = int(new_age)
        
        try:
            self.session.commit()
            print(f"✅ Creature updated successfully!")
            
            # Regenerate image if name changed
            if new_name:
                print("🎨 Regenerating creature image...")
                image_path, message = self.image_generator.generate_creature_image(creature.name, creature.species.name)
                if image_path:
                    creature.image_path = image_path
                    self.session.commit()
                    print(f"🖼️  {message}")
                
        except Exception as e:
            print(f"❌ Error updating creature: {e}")
            self.session.rollback()
    
    def delete_creature(self):
        """Delete a creature"""
        creatures = self.session.query(Creature).all()
        
        if not creatures:
            print("\n📝 No creatures found.")
            return
        
        print("\nSelect creature to delete:")
        for i, creature in enumerate(creatures, 1):
            habitat_count = len(creature.habitats)
            print(f"{i}. {creature.name} ({creature.species.name}) - In {habitat_count} habitat(s)")
        
        choice = get_user_choice(len(creatures))
        creature = creatures[choice - 1]
        
        confirm = input(f"Are you sure you want to delete '{creature.name}'? (y/N): ").lower()
        if confirm != 'y':
            print("Deletion cancelled.")
            return
        
        try:
            # Remove image file if it exists
            if creature.image_path and os.path.exists(creature.image_path):
                os.remove(creature.image_path)
            
            self.session.delete(creature)
            self.session.commit()
            print(f"✅ Creature '{creature.name}' deleted successfully!")
        except Exception as e:
            print(f"❌ Error deleting creature: {e}")
            self.session.rollback()
    
    def manage_habitats(self):
        """Habitat management submenu"""
        while True:
            options = [
                "Create a new habitat",
                "View all habitats",
                "Find habitat by biome type",
                "View creatures in specific habitat",
                "Update habitat",
                "Delete habitat"
            ]
            
            print_menu("Habitat Management", options)
            choice = get_user_choice(len(options) + 1)
            
            if choice == 1:
                self.create_habitat()
            elif choice == 2:
                self.view_all_habitats()
            elif choice == 3:
                self.find_habitat_by_biome()
            elif choice == 4:
                self.view_habitat_creatures()
            elif choice == 5:
                self.update_habitat()
            elif choice == 6:
                self.delete_habitat()
            elif choice == len(options) + 1:
                break
    
    def create_habitat(self):
        """Create a new habitat"""
        print("\n--- Create New Habitat ---")
        
        try:
            name = input("Habitat name: ").strip()
            if not name:
                print("Habitat name cannot be empty!")
                return
            
            # Check if habitat already exists
            existing = self.session.query(Habitat).filter_by(name=name).first()
            if existing:
                print(f"Habitat '{name}' already exists!")
                return
            
            biome_type = input("Biome type (e.g., Grassland, Forest, Aquatic, Desert): ").strip()
            if not biome_type:
                print("Biome type cannot be empty!")
                return
            
            square_footage = input("Square footage: ").strip()
            if not square_footage.isdigit():
                print("Square footage must be a number!")
                return
            
            square_footage = int(square_footage)
            
            # Create habitat
            habitat = Habitat(
                name=name,
                biome_type=biome_type,
                square_footage=square_footage
            )
            
            self.session.add(habitat)
            self.session.commit()
            
            print(f"✅ Habitat '{name}' created successfully!")
            
        except Exception as e:
            print(f"❌ Error creating habitat: {e}")
            self.session.rollback()
    
    def view_all_habitats(self):
        """View all habitats with capacity information"""
        habitats = self.session.query(Habitat).all()
        
        if not habitats:
            print("\n📝 No habitats found.")
            return
        
        print(f"\n🏞️  All Habitats ({len(habitats)} total)")
        print("-" * 80)
        
        for habitat in habitats:
            capacity_bar = format_capacity_bar(habitat.current_capacity, habitat.square_footage)
            status = "🔴 FULL" if habitat.is_full else "🟢 Available"
            
            print(f"• {habitat.name} ({habitat.biome_type})")
            print(f"  Capacity: {capacity_bar} {status}")
            print(f"  Residents: {len(habitat.creatures)} creatures")
            print()
    
    def find_habitat_by_biome(self):
        """Find habitats by biome type"""
        biome = input("\nEnter biome type to search: ").strip()
        if not biome:
            return
        
        habitats = self.session.query(Habitat).filter(Habitat.biome_type.ilike(f"%{biome}%")).all()
        
        if not habitats:
            print(f"\n📝 No habitats found matching biome '{biome}'.")
            return
        
        print(f"\n🔍 Found {len(habitats)} habitat(s) matching '{biome}':")
        print("-" * 60)
        
        for habitat in habitats:
            print_habitat_report(habitat)
    
    def view_habitat_creatures(self):
        """View creatures in a specific habitat"""
        habitats = self.session.query(Habitat).all()
        
        if not habitats:
            print("\n📝 No habitats found.")
            return
        
        print("\nSelect habitat to view:")
        for i, habitat in enumerate(habitats, 1):
            print(f"{i}. {habitat.name} ({len(habitat.creatures)} creatures)")
        
        choice = get_user_choice(len(habitats))
        selected_habitat = habitats[choice - 1]
        
        print_habitat_report(selected_habitat)
        
        if selected_habitat.creatures:
            print("\nDetailed creature information:")
            for creature in selected_habitat.creatures:
                print_creature_details(creature)
    
    def update_habitat(self):
        """Update habitat information"""
        habitats = self.session.query(Habitat).all()
        
        if not habitats:
            print("\n📝 No habitats found.")
            return
        
        print("\nSelect habitat to update:")
        for i, habitat in enumerate(habitats, 1):
            print(f"{i}. {habitat.name} ({habitat.biome_type})")
        
        choice = get_user_choice(len(habitats))
        habitat = habitats[choice - 1]
        
        print(f"\nUpdating: {habitat.name}")
        print("(Press Enter to keep current value)")
        
        new_name = input(f"Name [{habitat.name}]: ").strip()
        if new_name:
            habitat.name = new_name
        
        new_biome = input(f"Biome type [{habitat.biome_type}]: ").strip()
        if new_biome:
            habitat.biome_type = new_biome
        
        new_footage = input(f"Square footage [{habitat.square_footage}]: ").strip()
        if new_footage and new_footage.isdigit():
            new_size = int(new_footage)
            current_capacity = habitat.current_capacity
            
            if new_size < current_capacity:
                print(f"⚠️  Warning: New size ({new_size}) is smaller than current capacity ({current_capacity})!")
                print("This would make the habitat overcrowded.")
                confirm = input("Continue anyway? (y/N): ").lower()
                if confirm != 'y':
                    print("Update cancelled.")
                    return
            
            habitat.square_footage = new_size
        
        try:
            self.session.commit()
            print(f"✅ Habitat updated successfully!")
        except Exception as e:
            print(f"❌ Error updating habitat: {e}")
            self.session.rollback()
    
    def delete_habitat(self):
        """Delete a habitat"""
        habitats = self.session.query(Habitat).all()
        
        if not habitats:
            print("\n📝 No habitats found.")
            return
        
        print("\nSelect habitat to delete:")
        for i, habitat in enumerate(habitats, 1):
            creature_count = len(habitat.creatures)
            print(f"{i}. {habitat.name} ({creature_count} creatures)")
        
        choice = get_user_choice(len(habitats))
        habitat = habitats[choice - 1]
        
        if habitat.creatures:
            print(f"⚠️  Cannot delete '{habitat.name}' - it has {len(habitat.creatures)} creatures!")
            print("Please remove all creatures first.")
            return
        
        confirm = input(f"Are you sure you want to delete '{habitat.name}'? (y/N): ").lower()
        if confirm != 'y':
            print("Deletion cancelled.")
            return
        
        try:
            self.session.delete(habitat)
            self.session.commit()
            print(f"✅ Habitat '{habitat.name}' deleted successfully!")
        except Exception as e:
            print(f"❌ Error deleting habitat: {e}")
            self.session.rollback()
    
    def view_habitat_reports(self):
        """Generate comprehensive habitat reports"""
        habitats = self.session.query(Habitat).all()
        
        if not habitats:
            print("\n📝 No habitats found.")
            return
        
        print_header("🏞️  HABITAT MANAGEMENT REPORTS")
        
        # Overall statistics
        total_creatures = self.session.query(Creature).count()
        assigned_creatures = self.session.query(Creature).filter(Creature.habitats.any()).count()
        unassigned_creatures = total_creatures - assigned_creatures
        
        print(f"\n📊 Overall Statistics:")
        print(f"  Total Habitats: {len(habitats)}")
        print(f"  Total Creatures: {total_creatures}")
        print(f"  Assigned Creatures: {assigned_creatures}")
        print(f"  Unassigned Creatures: {unassigned_creatures}")
        
        # Capacity status report
        print(f"\n📈 Capacity Status Report:")
        print("-" * 70)
        
        full_habitats = []
        empty_habitats = []
        
        for habitat in habitats:
            capacity_bar = format_capacity_bar(habitat.current_capacity, habitat.square_footage, 25)
            
            if habitat.current_capacity == 0:
                status = "🔵 EMPTY"
                empty_habitats.append(habitat)
            elif habitat.is_full:
                status = "🔴 FULL"
                full_habitats.append(habitat)
            elif habitat.capacity_percentage > 80:
                status = "🟡 NEAR FULL"
            else:
                status = "🟢 AVAILABLE"
            
            print(f"  {habitat.name}: {capacity_bar} {status}")
        
        # Alerts
        if full_habitats:
            print(f"\n🚨 ATTENTION REQUIRED - Full Habitats ({len(full_habitats)}):")
            for habitat in full_habitats:
                print(f"  • {habitat.name} - {len(habitat.creatures)} creatures, {habitat.current_capacity}/{habitat.square_footage} sq ft")
        
        if empty_habitats:
            print(f"\n💡 Available Space - Empty Habitats ({len(empty_habitats)}):")
            for habitat in empty_habitats:
                print(f"  • {habitat.name} ({habitat.biome_type}) - {habitat.square_footage} sq ft available")
        
        # Diet distribution
        carnivores = self.session.query(Creature).join(Species).filter(Species.diet_type == "Carnivore").count()
        herbivores = self.session.query(Creature).join(Species).filter(Species.diet_type == "Herbivore").count()
        omnivores = self.session.query(Creature).join(Species).filter(Species.diet_type == "Omnivore").count()
        
        print(f"\n🍽️  Diet Distribution:")
        print(f"  Carnivores: {carnivores}")
        print(f"  Herbivores: {herbivores}")
        print(f"  Omnivores: {omnivores}")
        
        # Unassigned creatures
        if unassigned_creatures > 0:
            unassigned = self.session.query(Creature).filter(~Creature.habitats.any()).all()
            print(f"\n🏠 Unassigned Creatures ({len(unassigned)}):")
            for creature in unassigned:
                print(f"  • {creature.name} ({creature.species.name}) - Size: {creature.size} sq ft")

def main():
    """Main entry point"""
    try:
        cli = CreatureCollectorCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()