from ortools.sat.python import cp_model
import pandas as pd
import numpy as np
from itertools import product


class SimpleScheduler:
    def __init__(self, employees, shifts, hours_per_shift):
        self.employees = employees
        self.shifts = shifts
        self.hours_per_shift = hours_per_shift  # Durée de chaque shift en heures
        self.model = cp_model.CpModel()
        self.shift_assignments = {}
        self.create_variables()
        self.shift_pref = {}
        self.create_prefs()
        self.set_objective()

    def create_variables(self):
        # Variables de décision : chaque employé peut travailler un shift ou non
        for employee in self.employees:
            for day, periods in self.shifts.items():
                for period in periods:
                    self.shift_assignments[(employee, day, period)] = self.model.NewBoolVar(f'{employee}_{day}_{period}')

    def add_constraints(self):
        # Contrainte 1 : chaque employé peut travailler au plus un shift par jour
        for employee in self.employees:
            for day in self.shifts.keys():
                self.model.Add(sum(self.shift_assignments[(employee, day, period)] for period in self.shifts[day]) <= 1)

        # Contrainte 2 : chaque shift doit avoir au moins un employé
        for day, periods in self.shifts.items():
            for period in periods:
                self.model.Add(sum(self.shift_assignments[(employee, day, period)] for employee in self.employees) >= 1)

        # Contrainte 3 : limite des heures de travail hebdomadaires (48 heures par semaine)
        for employee in self.employees:
            total_hours = sum(self.shift_assignments[(employee, day, period)] * self.hours_per_shift[period] 
                              for day, periods in self.shifts.items() for period in periods)
            self.model.Add(total_hours <= 48)
        
        # Contrainte 6 : un dimanche de repos toutes les 2 semaines
        for employee in self.employees:
            for week_start in range(0, len(self.shifts), 14):  # Périodes de 2 semaines
                sunday_shifts = [
                    self.shift_assignments[(employee, 'Dimanche', period)] for period in self.shifts['Dimanche']
                ]
                self.model.Add(sum(sunday_shifts) <= 1)

    def set_objective(self):
        # Minimize the sum of preferences for assigned shifts
        total_pref_expr = sum(self.shift_pref[(employee, shift)] * self.shift_assignments[(employee, shift)]
                            for employee, shift in product(self.employees, self.shifts))
        self.model.Minimize(total_pref_expr)

        # Contrainte 5 : périodes de repos minimum de 11 heures entre deux shifts
        # Si un employé travaille un shift, il ne peut pas travailler un shift le même jour ou suivant immédiatement
        for employee in self.employees:
            for day, periods in self.shifts.items():
                for i, period1 in enumerate(periods):
                    for j, period2 in enumerate(periods):
                        if i < j:  # Pour éviter les conflits directs de shifts
                            self.model.AddBoolOr([
                                self.shift_assignments[(employee, day, period1)].Not(),
                                self.shift_assignments[(employee, day, period2)].Not()
                            ])
    

    def create_prefs(self):
        for employee in self.employees:
            for shift in self.shifts:
                self.shift_pref[(employee, shift, )] = np.random.randint(1, 50)


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
                for day, periods in self.shifts.items():
                    assigned_shift = '-'
                    for period in periods:
                        if solver.Value(self.shift_assignments[(employee, day, period)]):
                            if period == 'Matin':
                                assigned_shift = 'M'
                            elif period == 'Soir':
                                assigned_shift = 'S'
                            elif period == 'Journee':
                                assigned_shift = 'J'
                            elif period == 'Nuit':
                                assigned_shift = 'N'
                    row.append(assigned_shift)
                results.append(row)

            # Créer un DataFrame avec les résultats
            df = pd.DataFrame(results, columns=["Employee"] + list(self.shifts.keys()))

            # Sauvegarder le DataFrame dans un fichier Excel
            df.to_excel(filename, index=False)
            print(f"Le planning a été sauvegardé dans le fichier '{filename}'")
        else:
            print("Aucune solution faisable trouvée.")

# Exemple d'utilisation
employees = ['Alice', 'Bob', 'Charlie', 'Illyes', 'Jimmy','Donatien','Fanny']

# Définition des shifts avec des périodes spécifiques (matin, soir, journée, nuit) pour chaque jour de la semaine
shifts = {
    'Lundi': ['Matin', 'Soir', 'Journee', 'Nuit'],
    'Mardi': ['Matin', 'Soir', 'Journee', 'Nuit'],
    'Mercredi': ['Matin', 'Soir', 'Journee', 'Nuit'],
    'Jeudi': ['Matin', 'Soir', 'Journee', 'Nuit'],
    'Vendredi': ['Matin', 'Soir', 'Journee', 'Nuit'],
    'Samedi': ['Matin', 'Soir', 'Journee', 'Nuit'],
    'Dimanche': ['Matin', 'Soir', 'Journee', 'Nuit']
}

# Durée des shifts en heures
hours_per_shift = {
    'Matin': 8,
    'Soir': 8,
    'Journee': 8,
    'Nuit': 10  # La nuit est plus longue dans ton exemple
}

scheduler = SimpleScheduler(employees, shifts, hours_per_shift)
scheduler.add_constraints()
scheduler.add_constraints2()
scheduler.solve_and_save('planning_infirmiers3.xlsx')
