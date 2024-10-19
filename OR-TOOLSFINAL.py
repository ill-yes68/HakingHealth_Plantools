from ortools.sat.python import cp_model
import pandas as pd
import numpy as np
from itertools import product
from datetime import datetime, timedelta

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
        self.add_constraints()  # Call this here to ensure constraints are added before setting the objective
        self.set_objective()

    def create_variables(self):
        # Variables de décision : chaque employé peut travailler un shift ou non
        for employee in self.employees:
            for day, periods in self.shifts.items():
                for period in periods:
                    self.shift_assignments[(employee, day, period)] = self.model.NewBoolVar(f'{employee}_{day}_{period}')

    def create_prefs(self):
        for employee in self.employees:
            for day in self.shifts:
                self.shift_pref[(employee, day)] = np.random.randint(1, 50)

    def add_constraints(self):
        # Contrainte 1 : chaque employé peut travailler au plus un shift par jour
        for employee in self.employees:
            for day in self.shifts.keys():
                self.model.Add(sum(self.shift_assignments[(employee, day, period)] for period in self.shifts[day]) <= 1)

        # Contrainte 2 : chaque shift doit avoir au moins un employé
        for day, periods in self.shifts.items():
            for period in periods:
                self.model.Add(sum(self.shift_assignments[(employee, day, period)] for employee in self.employees) >= 1)

        # Contrainte 3 : limite des heures de travail mensuelles (192 heures par mois)
        for employee in self.employees:
            total_hours = sum(self.shift_assignments[(employee, day, period)] * self.hours_per_shift[period] 
                              for day in self.shifts for period in self.shifts[day])
            self.model.Add(total_hours <= 192)  # Assuming 24 days of shifts in a month

        # Contrainte 4 : un jour de repos toutes les 2 semaines
        for employee in self.employees:
            for day_offset in range(0, 30, 14):  # Périodes de 2 semaines
                rest_days = ['Dimanche']  # You can expand this for other days as necessary
                for rest_day in rest_days:
                    if rest_day in self.shifts:
                        self.model.Add(sum(self.shift_assignments[(employee, rest_day, period)] for period in self.shifts[rest_day]) <= 1)

        # Contrainte 5 : périodes de repos minimum de 11 heures entre deux shifts
        for employee in self.employees:
            for day, periods in self.shifts.items():
                for i, period1 in enumerate(periods):
                    for j, period2 in enumerate(periods):
                        if i < j:  # Pour éviter les conflits directs de shifts
                            self.model.AddBoolOr([
                                self.shift_assignments[(employee, day, period1)].Not(),
                                self.shift_assignments[(employee, day, period2)].Not()
                            ])

    def set_objective(self):
        # Minimize the sum of preferences for assigned shifts
        total_pref_expr = sum(
            self.shift_pref[(employee, day)] * self.shift_assignments[(employee, day, period)]
            for employee in self.employees
            for day in self.shifts
            for period in self.shifts[day]
        )
        self.model.Minimize(total_pref_expr)

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
                for day in self.shifts.keys():
                    assigned_shift = '-'
                    for period in self.shifts[day]:
                        if solver.Value(self.shift_assignments[(employee, day, period)]):
                            assigned_shift = {'Matin': 'M', 'Soir': 'S', 'Journee': 'J', 'Nuit': 'N'}.get(period, '-')
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
employees = ['Alice', 'Bob', 'Charlie', 'Illyes', 'Jimmy', 'Donatien', 'Fanny']

# Définition des shifts avec des périodes spécifiques (matin, soir, journée, nuit) pour chaque jour du mois
days_in_month = [f'Jour {i+1}' for i in range(30)]  # Adjust as needed for the month length
shifts = {day: ['Matin', 'Soir', 'Journee', 'Nuit'] for day in days_in_month}

# Durée des shifts en heures
hours_per_shift = {
    'Matin': 8,
    'Soir': 8,
    'Journee': 8,
    'Nuit': 10  # La nuit est plus longue dans ton exemple
}

scheduler = SimpleScheduler(employees, shifts, hours_per_shift)
scheduler.solve_and_save('planning_infirmiers_month31.xlsx')
