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
        # Contrainte 1 : chaque employé peut travailler au plus un shift par jour
        for employee in self.employees:
            self.model.Add(sum(self.shift_assignments[(employee, shift)] for shift in self.shifts) <= len(self.shifts))

        # Contrainte 2 : chaque shift doit avoir au moins un employé
        for shift in self.shifts:
            self.model.Add(sum(self.shift_assignments[(employee, shift)] for employee in self.employees) >= 1)

        # Contrainte 3 : limite des heures de travail hebdomadaires (48 heures par semaine)
        for employee in self.employees:
            total_hours = sum(self.shift_assignments[(employee, shift)] * self.hours_per_shift for shift in self.shifts)
            self.model.Add(total_hours <= 48)

        # Contrainte 4 : limite des heures de travail mensuelles (174 heures par mois)
        for employee in self.employees:
            total_hours = sum(self.shift_assignments[(employee, shift)] * self.hours_per_shift for shift in self.shifts)
            self.model.Add(total_hours <= 174)

        # Contrainte 5 : périodes de repos minimum de 11 heures entre deux shifts
        # Ici, nous devons vérifier que deux shifts ne se suivent pas directement
        for i, shift1 in enumerate(self.shifts):
            for j, shift2 in enumerate(self.shifts):
                if i < j:
                    # Suppose que les shifts sont dans l'ordre et qu'il y a au moins 11h entre deux shifts distincts
                    self.model.AddBoolOr([
                        self.shift_assignments[(employee, shift1)].Not(),
                        self.shift_assignments[(employee, shift2)].Not()
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
shifts = ['Lundi matin', 'Lundi après-midi', 'Mardi matin','Mardi après-midi','mercredi matin','mercredi apres-midi','jeudi  matin','jeudi apres-midi','vendredi matin','vendredi apres-midi']
hours_per_shift = 8  # Par exemple, chaque shift dure 8 heures

scheduler = SimpleScheduler(employees, shifts, hours_per_shift)
scheduler.add_constraints()
scheduler.solve_and_save('planning_infirmiers.xlsx')
