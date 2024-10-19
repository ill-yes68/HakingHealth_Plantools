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
            for week in self.shifts:
                for day, periods in self.shifts[week].items():
                    for period in periods:
                        self.shift_assignments[(employee, week, day, period)] = self.model.NewBoolVar(f'{employee}_week{week}_{day}_{period}')

    def add_constraints(self):
        # Contrainte 1 : chaque employé peut travailler au plus un shift par jour
        for employee in self.employees:
            for week in self.shifts:
                for day in self.shifts[week].keys():
                    self.model.Add(sum(self.shift_assignments[(employee, week, day, period)] for period in self.shifts[week][day]) <= 1)

        # Contrainte 2 : chaque shift doit avoir au moins un employé
        for week in self.shifts:
            for day, periods in self.shifts[week].items():
                for period in periods:
                    self.model.Add(sum(self.shift_assignments[(employee, week, day, period)] for employee in self.employees) >= 1)

        # Contrainte 3 : limite des heures de travail hebdomadaires (48 heures par semaine)
        for employee in self.employees:
            for week in self.shifts:
                total_hours = sum(self.shift_assignments[(employee, week, day, period)] * self.hours_per_shift[period] 
                                  for day, periods in self.shifts[week].items() for period in periods)
                self.model.Add(total_hours <= 48)

        # Contrainte 4 : limite des heures de travail mensuelles (174 heures par mois)
        total_hours_month = sum(self.shift_assignments[(employee, week, day, period)] * self.hours_per_shift[period] 
                                for employee in self.employees 
                                for week in self.shifts 
                                for day, periods in self.shifts[week].items() for period in periods)
        for employee in self.employees:
            self.model.Add(total_hours_month <= 174)

        # Contrainte 5 : périodes de repos minimum de 11 heures entre deux shifts
        for employee in self.employees:
            for week in self.shifts:
                for day, periods in self.shifts[week].items():
                    for i, period1 in enumerate(periods):
                        for j, period2 in enumerate(periods):
                            if i < j:  # Pour éviter les conflits directs de shifts
                                self.model.AddBoolOr([
                                    self.shift_assignments[(employee, week, day, period1)].Not(),
                                    self.shift_assignments[(employee, week, day, period2)].Not()
                                ])

        # Contrainte : un dimanche de repos toutes les 2 semaines
        for employee in self.employees:
            for week_start in range(1, 5, 2):  # Vérification pour les dimanches sur chaque bloc de 2 semaines
                sunday_shifts_week1 = [self.shift_assignments[(employee, week_start, 'Dimanche', period)] 
                                       for period in self.shifts[week_start]['Dimanche']]
                sunday_shifts_week2 = [self.shift_assignments[(employee, week_start + 1, 'Dimanche', period)] 
                                       for period in self.shifts[week_start + 1]['Dimanche']]
                self.model.Add(sum(sunday_shifts_week1) + sum(sunday_shifts_week2) <= 1)

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
                for week in self.shifts:
                    for day, periods in self.shifts[week].items():
                        assigned_shift = '-'
                        for period in periods:
                            if solver.Value(self.shift_assignments[(employee, week, day, period)]):
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
            columns = ["Employee"] + [f"Semaine {week} - {day}" for week in self.shifts for day in self.shifts[week].keys()]
            df = pd.DataFrame(results, columns=columns)

            # Sauvegarder le DataFrame dans un fichier Excel
            df.to_excel(filename, index=False)
            print(f"Le planning a été sauvegardé dans le fichier '{filename}'")
        else:
            print("Aucune solution faisable trouvée.")

# Exemple d'utilisation
employees = ['Alice', 'Bob', 'Charlie', 'Illyes', 'Jimmy','Donatien','Fanny','betrand','nikola','hugo']

# Définir les shifts pour un mois (4 semaines)
shifts = {
    1: {  # Semaine 1
        'Lundi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Mardi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Mercredi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Jeudi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Vendredi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Samedi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Dimanche': ['Matin', 'Soir', 'Journee', 'Nuit']
    },
    2: {  # Semaine 2
        'Lundi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Mardi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Mercredi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Jeudi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Vendredi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Samedi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Dimanche': ['Matin', 'Soir', 'Journee', 'Nuit']
    },
    3: {  # Semaine 3
        'Lundi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Mardi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Mercredi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Jeudi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Vendredi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Samedi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Dimanche': ['Matin', 'Soir', 'Journee', 'Nuit']
    },
    4: {  # Semaine 4
        'Lundi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Mardi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Mercredi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Jeudi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Vendredi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Samedi': ['Matin', 'Soir', 'Journee', 'Nuit'],
        'Dimanche': ['Matin', 'Soir', 'Journee', 'Nuit']
    }
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
scheduler.solve_and_save('planning_infirmiers_mois.xlsx')
