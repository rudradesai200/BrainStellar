import json

PUZZLES_JSON = 'puzzles.json'
TEX_FILE = '../tex/book.tex'

def create_latex_for_puzzle(puzzle: dict):
    question = "\item %s\n\small\emph{(Category: %s)}\n" % (puzzle['Question'],puzzle['category'])
    if "Hint" in puzzle.keys():
        question += "\n\small\emph{Hint: %s}\n\n" % (puzzle['Hint'])
    
    solution = "\item"
    if puzzle.get('Answer', '') != '':
        solution += f"\nAnswer: {puzzle.get('Answer','')}\n "
    solution += f"\nSolution: {puzzle.get('Solution','')}\n"
    return question, solution

if __name__ == "__main__":
    fp = open(PUZZLES_JSON, "r")
    puzzles = json.load(fp)
    
    qfp = open(TEX_FILE, "w")
    qfp.write(
"""\section{Questions}
\\begin{enumerate}
""")
    solutions = []
    for i, puzzle in enumerate(puzzles):
        question, solution = create_latex_for_puzzle(puzzle)
        qfp.write(f"% --------------------------  Question {i+1} starts  -------------------------- \n\n")
        qfp.write(question)
        qfp.write(f"% --------------------------  Question {i+1} ends    --------------------------\n\n\n\n")
        solutions.append(solution)

    qfp.write(
"""\end{enumerate}
\\newpage
\section{Solutions}
\\begin{enumerate}
""")

    for i, solution in enumerate(solutions):
        qfp.write(f"% --------------------------  Question {i+1} starts  -------------------------- \n\n")
        qfp.write(solution)
        qfp.write(f"% --------------------------  Question {i+1} ends    --------------------------\n\n\n\n")
    
    qfp.write("\end{enumerate}")

    fp.close()
    qfp.close()