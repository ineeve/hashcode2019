from __future__ import print_function
from ortools.linear_solver import pywraplp

def main():
  solver = pywraplp.Solver('SolveIntegerProblem',
                           pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

  # c1,c2,c3 and c4 are integer non-negative variables.
  c1 = solver.IntVar(0.0, solver.infinity(), 'c1')
  c2 = solver.IntVar(0.0, solver.infinity(), 'c2')
  c3 = solver.IntVar(0.0, solver.infinity(), 'c3')
  c4 = solver.IntVar(0.0, solver.infinity(), 'c4')

  # c1 >= 50
  constraint1 = solver.Constraint(50, solver.infinity())
  constraint1.SetCoefficient(c1, 1)
  constraint1.SetCoefficient(c2, 0)
  constraint1.SetCoefficient(c3, 0)
  constraint1.SetCoefficient(c4, 0)

  # 2c2 + c3 >= 80
  constraint2 = solver.Constraint(80, solver.infinity())
  constraint2.SetCoefficient(c1, 0)
  constraint2.SetCoefficient(c2, 2)
  constraint2.SetCoefficient(c3, 1)
  constraint2.SetCoefficient(c4, 0)

  
  # c1 + 2c3 + 4c4 >= 200
  constraint3 = solver.Constraint(200, solver.infinity())
  constraint3.SetCoefficient(c1, 1)
  constraint3.SetCoefficient(c2, 0)
  constraint3.SetCoefficient(c3, 2)
  constraint3.SetCoefficient(c4, 4)

  # Minimize c1 + c2 + c3 + c4
  objective = solver.Objective()
  objective.SetCoefficient(c1, 1)
  objective.SetCoefficient(c2, 1)
  objective.SetCoefficient(c3, 1)
  objective.SetCoefficient(c4, 1)
  objective.SetMinimization()

  """Solve the problem and print the solution."""
  result_status = solver.Solve()
  # The problem has an optimal solution.
  assert result_status == pywraplp.Solver.OPTIMAL

  # The solution looks legit (when using solvers other than
  # GLOP_LINEAR_PROGRAMMING, verifying the solution is highly recommended!).
  assert solver.VerifySolution(1e-7, True)

  print('Number of variables =', solver.NumVariables())
  print('Number of constraints =', solver.NumConstraints())

  # The objective value of the solution.
  print('Optimal objective value = %d' % solver.Objective().Value())
  print()
  # The value of each variable in the solution.
  variable_list = [c1, c2, c3, c4]

  for variable in variable_list:
    print('%s = %d' % (variable.name(), variable.solution_value()))

if __name__ == '__main__':
  main()