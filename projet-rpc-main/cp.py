import argparse
from ortools.sat.python import cp_model


def solve_distribution_with_rotation(L, W, H, objects, output_file):
    model = cp_model.CpModel()
    num_objects = len(objects)

    # Variables
    x = [model.NewIntVar(0, L, f'x_{i}') for i in range(num_objects)]
    y = [model.NewIntVar(0, W, f'y_{i}') for i in range(num_objects)]
    z = [model.NewIntVar(0, H, f'z_{i}') for i in range(num_objects)]
    v = [model.NewIntVar(0, num_objects - 1, f'v_{i}') for i in range(num_objects)]  # Identifiant du véhicule

    # Variables pour les dimensions effectives et les orientations actives
    active_orientation = [
        [model.NewBoolVar(f'orientation_{i}_{j}') for j in range(6)]
        for i in range(num_objects)
    ]
    L_eff = [model.NewIntVar(0, L, f'L_eff_{i}') for i in range(num_objects)]
    W_eff = [model.NewIntVar(0, W, f'W_eff_{i}') for i in range(num_objects)]
    H_eff = [model.NewIntVar(0, H, f'H_eff_{i}') for i in range(num_objects)]

    # Contraindre une seule orientation active par objet
    for i in range(num_objects):
        model.Add(sum(active_orientation[i]) == 1)

        # Définir les orientations possibles pour l'objet i
        orientations = [
            (objects[i][0], objects[i][1], objects[i][2]),  # Original: (L, W, H)
            (objects[i][0], objects[i][2], objects[i][1]),  # Rotation 1
            (objects[i][1], objects[i][0], objects[i][2]),  # Rotation 2
            (objects[i][1], objects[i][2], objects[i][0]),  # Rotation 3
            (objects[i][2], objects[i][0], objects[i][1]),  # Rotation 4
            (objects[i][2], objects[i][1], objects[i][0])   # Rotation 5
        ]

        for j, (L2, W2, H2) in enumerate(orientations):
            model.Add(L_eff[i] == L2).OnlyEnforceIf(active_orientation[i][j])
            model.Add(W_eff[i] == W2).OnlyEnforceIf(active_orientation[i][j])
            model.Add(H_eff[i] == H2).OnlyEnforceIf(active_orientation[i][j])

    # Contraintes : Les objets doivent tenir dans les dimensions du véhicule
    for i in range(num_objects):
        model.Add(x[i] + L_eff[i] <= L)  # Longueur
        model.Add(y[i] + W_eff[i] <= W)  # Largeur
        model.Add(z[i] + H_eff[i] <= H)  # Hauteur

        # Forcer les coordonnées à être positives ou zéro
        model.Add(x[i] >= 0)
        model.Add(y[i] >= 0)
        model.Add(z[i] >= 0)

    # Contraintes de non-chevauchement
    for i in range(num_objects):
        for j in range(i + 1, num_objects):
            same_vehicle = model.NewBoolVar(f'same_vehicle_{i}_{j}')
            model.Add(v[i] == v[j]).OnlyEnforceIf(same_vehicle)
            model.Add(v[i] != v[j]).OnlyEnforceIf(same_vehicle.Not())

            left = model.NewBoolVar(f'left_{i}_{j}')
            right = model.NewBoolVar(f'right_{i}_{j}')
            front = model.NewBoolVar(f'front_{i}_{j}')
            back = model.NewBoolVar(f'back_{i}_{j}')
            below = model.NewBoolVar(f'below_{i}_{j}')
            above = model.NewBoolVar(f'above_{i}_{j}')

            model.Add(x[i] + L_eff[i] <= x[j]).OnlyEnforceIf(left)
            model.Add(x[j] + L_eff[j] <= x[i]).OnlyEnforceIf(right)
            model.Add(y[i] + W_eff[i] <= y[j]).OnlyEnforceIf(front)
            model.Add(y[j] + W_eff[j] <= y[i]).OnlyEnforceIf(back)
            model.Add(z[i] + H_eff[i] <= z[j]).OnlyEnforceIf(below)
            model.Add(z[j] + H_eff[j] <= z[i]).OnlyEnforceIf(above)

            model.AddBoolOr([left, right, front, back, below, above]).OnlyEnforceIf(same_vehicle)

    # Contraintes d'empilement (uniquement sur un objet ou à la base)
    for i in range(num_objects):
        at_base = model.NewBoolVar(f'at_base_{i}')
        model.Add(z[i] == 0).OnlyEnforceIf(at_base)

        stacked_on_another = model.NewBoolVar(f'stacked_on_another_{i}')
        stack_conditions = []

        for j in range(num_objects):
            if i != j:
                condition = model.NewBoolVar(f'stack_{i}_on_{j}')
                stack_conditions.append(condition)

                model.Add(z[i] == z[j] + H_eff[j]).OnlyEnforceIf(condition)
                model.Add(x[i] >= x[j]).OnlyEnforceIf(condition)
                model.Add(x[i] + L_eff[i] <= x[j] + L_eff[j]).OnlyEnforceIf(condition)
                model.Add(y[i] >= y[j]).OnlyEnforceIf(condition)
                model.Add(y[i] + W_eff[i] <= y[j] + W_eff[j]).OnlyEnforceIf(condition)

        model.AddBoolOr(stack_conditions).OnlyEnforceIf(stacked_on_another)
        model.AddBoolOr([at_base, stacked_on_another])

    # Objectif : Minimiser le nombre de véhicules utilisés + favoriser les coordonnées minimales
    max_vehicle = model.NewIntVar(0, num_objects - 1, "max_vehicle")
    model.AddMaxEquality(max_vehicle, v)

    model.Minimize(max_vehicle * 10000 + sum(x) + sum(y) + sum(z))

    # Résolution
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 600  # Limite à 10 minutes
    status = solver.Solve(model)

    # Écriture des résultats dans le fichier de sortie
    with open(output_file, "w") as f:
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            f.write("SAT\n")
            for i in range(num_objects):
                f.write(
                    f"{solver.Value(v[i])} {solver.Value(x[i])} {solver.Value(y[i])} {solver.Value(z[i])} "
                    f"{solver.Value(x[i]) + solver.Value(L_eff[i])} "
                    f"{solver.Value(y[i]) + solver.Value(W_eff[i])} "
                    f"{solver.Value(z[i]) + solver.Value(H_eff[i])}\n"
                )
        else:
            f.write("UNSAT\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve a bin-packing problem using CP-SAT.")
    parser.add_argument("input", help="Input file containing dimensions and objects.")
    parser.add_argument("output", help="Output file for the solution.")
    args = parser.parse_args()

    # Lire les dimensions et les objets à partir du fichier d'entrée
    with open(args.input, "r") as file:
        lines = file.readlines()

    L, W, H = map(int, lines[0].strip().split())
    num_objects = int(lines[1].strip())
    objects = [tuple(map(int, line.strip().split())) for line in lines[2:2 + num_objects]]

    # Résolution
    solve_distribution_with_rotation(L, W, H, objects, args.output)
