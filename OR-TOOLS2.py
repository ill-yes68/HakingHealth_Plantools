from ortools.sat.python import cp_model
import pandas as pd

class SimpleScheduler:
    def __init__(self, employees, shifts, hours_per_shift):
        self.employees = employees
        self.shifts = shifts
        self.hours_per_shift = hours_per_shift  # Durée de chaque shift en heures
        self.model = cp_model.CpModel()
        self.shift_assignments = {}
        self.create_variables()

    def create_variables(self):
        # Variables de décision : chaque employé peut travailler un shift ou non
        for employee in self.employees:
            for shift in self.shifts:
                self.shift_assignments[(employee, shift)] = self.model.NewBoolVar(f'{employee}_{shift}')

    def add_constraints(self):
        # Contrainte : chaque employé peut travailler au plus un shift par jour
        for employee in self.employees:
            self.model.Add(sum(self.shift_assignments[(employee, shift)] for shift in self.shifts) <= len(self.shifts))

        # Contrainte : chaque shift doit avoir au moins un employé
        for shift in self.shifts:
            self.model.Add(sum(self.shift_assignments[(employee, shift)] for employee in self.employees) >= 1)

        # Contrainte : limite des heures de travail hebdomadaires (48 heures par semaine)
        for employee in self.employees:
            total_hours = sum(self.shift_assignments[(employee, shift)] * self.hours_per_shift for shift in self.shifts)
            self.model.Add(total_hours <= 48)

        # Contrainte : limite des heures de travail mensuelles (174 heures par mois)
        for employee in self.employees:
            total_hours = sum(self.shift_assignments[(employee, shift)] * self.hours_per_shift for shift in self.shifts)
            self.model.Add(total_hours <= 174)

        # Contrainte : respect des 11 heures de pause entre un shift d'après-midi et le shift du matin suivant
        # Nous devons définir des paires après-midi/matin sur des jours consécutifs
        pairs_to_avoid = [
            ("Lundi après-midi", "Mardi matin"),
            ("Mardi après-midi", "Mercredi matin"),
            ("Mercredi après-midi", "Jeudi matin"),
            ("Jeudi après-midi", "Vendredi matin")
        ]
        
        for employee in self.employees:
            for (afternoon_shift, next_morning_shift) in pairs_to_avoid:
                self.model.AddBoolOr([
                    self.shift_assignments[(employee, afternoon_shift)].Not(),
                    self.shift_assignments[(employee, next_morning_shift)].Not()
                ])

    def solve_and_save(self, filename='planning.xlsx'):
        # Résoudre le modèle
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            # Créer une liste pour stocker les résultats
            results = []

            # Afficher les assignations et stocker dans la liste
            for employee in self.employees:
                row = [employee]  # L'employé est la première colonne
                for shift in self.shifts:
                    if solver.Value(self.shift_assignments[(employee, shift)]):
                        row.append("X")  # X si l'employé est assigné à ce shift
                    else:
                        row.append("-")  # - si non
                results.append(row)

            # Créer un DataFrame avec les résultats
            df = pd.DataFrame(results, columns=["Employee"] + self.shifts)

            # Sauvegarder le DataFrame dans un fichier Excel
            df.to_excel(filename, index=False)
            print(f"Le planning a été sauvegardé dans le fichier '{filename}'")
        else:
            print("Aucune solution faisable trouvée.")

# Exemple d'utilisation
employees = ['Alice', 'Bob', 'Charlie']
shifts = ['Lundi matin', 'Lundi après-midi', 'Mardi matin', 'Mardi après-midi', 'Mercredi matin', 
          'Mercredi après-midi', 'Jeudi matin', 'Jeudi après-midi', 'Vendredi matin', 'Vendredi après-midi']
hours_per_shift = 8  # Par exemple, chaque shift dure 8 heures

scheduler = SimpleScheduler(employees, shifts, hours_per_shift)
scheduler.add_constraints()
scheduler.solve_and_save('planning_infirmiers2.xlsx')
