# convert_to_latex.py
# Converts equation outputs from step1.py into regular mathematical syntax (LaTeX)

import sys
import re
import subprocess
from io import StringIO

try:
    import sympy as sp
    from sympy.printing.latex import latex
except ImportError:
    print("Error: sympy is required. Please install it with: pip install sympy")
    sys.exit(1)


def convert_sympy_output_to_latex():
    """
    Runs step1.py, captures its output, and converts SymPy expressions to LaTeX.
    """
    print("Running step1.py and converting outputs to LaTeX format...\n")
    print("=" * 70)
    
    # Read and execute step1.py while suppressing print statements
    # This avoids Unicode encoding issues with print statements
    try:
        # Read step1.py
        with open('step1.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Comment out all print statements to avoid encoding issues
        lines = code.split('\n')
        modified_lines = []
        for line in lines:
            # Comment out lines that contain print statements
            if 'print(' in line and not line.strip().startswith('#'):
                # Indent the comment to match original indentation
                indent = len(line) - len(line.lstrip())
                modified_lines.append(' ' * indent + '# ' + line.lstrip())
            else:
                modified_lines.append(line)
        
        code = '\n'.join(modified_lines)
        
        # Execute the modified code in a namespace
        namespace = {}
        exec(compile(code, 'step1.py', 'exec'), namespace)
        
        # Get the Gamma array
        Γ = namespace['Gamma']
        
    except FileNotFoundError:
        print("Error: Could not find step1.py. Make sure it's in the same directory.")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing step1.py: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Define the Christoffel symbols to convert (same as in step1.py)
    symbols_to_print = [
        ((0, 0, 0), r'\Gamma^t_{tt}'),
        ((0, 0, 1), r'\Gamma^t_{tr}'),
        ((0, 1, 1), r'\Gamma^t_{rr}'),
        ((1, 0, 0), r'\Gamma^r_{tt}'),
        ((1, 0, 1), r'\Gamma^r_{tr}'),
        ((1, 1, 1), r'\Gamma^r_{rr}'),
        ((2, 1, 2), r'\Gamma^\theta_{r\theta}'),
        ((1, 2, 2), r'\Gamma^r_{\theta\theta}'),
        ((3, 1, 3), r'\Gamma^\phi_{r\phi}'),
        ((1, 3, 3), r'\Gamma^r_{\phi\phi}'),
        ((2, 3, 3), r'\Gamma^\theta_{\phi\phi}'),
        ((3, 2, 3), r'\Gamma^\phi_{\theta\phi}'),
    ]
    
    print("Christoffel Symbols in LaTeX format:\n")
    
    for indices, latex_name in symbols_to_print:
        mu, nu, rho = indices
        expr = Γ[mu][nu][rho]
        
        # Convert to LaTeX with better formatting
        # Use mode='inline' for better function representation
        latex_expr = latex(expr, mode='plain')
        
        # Replace alpha with function arguments with just α
        latex_expr = re.sub(r'\\alpha\{t,r\s*\}', r'\\alpha', latex_expr)
        latex_expr = re.sub(r'\\alpha\{\\left\(t,r\s*\\right\)\}', r'\\alpha', latex_expr)
        latex_expr = re.sub(r'\\alpha\\left\(t, r\\right\)', r'\\alpha', latex_expr)
        latex_expr = re.sub(r'\\alpha\{\\left\(t,\s*r\s*\\right\)\}', r'\\alpha', latex_expr)
        latex_expr = re.sub(r'\\operatorname\{alpha\}\\left\(t, r\\right\)', r'\\alpha', latex_expr)
        
        # Replace beta with function arguments with just β
        latex_expr = re.sub(r'\\beta\{t,r\s*\}', r'\\beta', latex_expr)
        latex_expr = re.sub(r'\\beta\{\\left\(t,r\s*\\right\)\}', r'\\beta', latex_expr)
        latex_expr = re.sub(r'\\beta\\left\(t, r\\right\)', r'\\beta', latex_expr)
        latex_expr = re.sub(r'\\beta\{\\left\(t,\s*r\s*\\right\)\}', r'\\beta', latex_expr)
        latex_expr = re.sub(r'\\operatorname\{beta\}\\left\(t, r\\right\)', r'\\beta', latex_expr)
        
        # Remove any remaining function argument patterns for alpha and beta
        latex_expr = re.sub(r'\\alpha\{[^}]+\}', r'\\alpha', latex_expr)
        latex_expr = re.sub(r'\\beta\{[^}]+\}', r'\\beta', latex_expr)
        
        # Replace partial derivatives: \frac{\partial}{\partial t} alpha -> \partial_t \alpha
        latex_expr = re.sub(
            r'\\frac\{\\partial\}\{\\partial\s+t\}\s*\\alpha',
            r'\\partial_t \\alpha',
            latex_expr
        )
        latex_expr = re.sub(
            r'\\frac\{\\partial\}\{\\partial\s+r\}\s*\\alpha',
            r'\\partial_r \\alpha',
            latex_expr
        )
        latex_expr = re.sub(
            r'\\frac\{\\partial\}\{\\partial\s+t\}\s*\\beta',
            r'\\partial_t \\beta',
            latex_expr
        )
        latex_expr = re.sub(
            r'\\frac\{\\partial\}\{\\partial\s+r\}\s*\\beta',
            r'\\partial_r \\beta',
            latex_expr
        )
        
        # Replace exp with e^
        latex_expr = re.sub(r'\\exp\\left\\(([^)]+)\\right\\)', r'e^{{\1}}', latex_expr)
        latex_expr = re.sub(r'e\^(-?\s*\d+)\s*', r'e^{{\1}}', latex_expr)
        
        # Replace sin and cos notation - fix escaped backslashes first
        latex_expr = latex_expr.replace(r'\\theta', r'\theta')
        latex_expr = latex_expr.replace(r'\\phi', r'\phi')
        latex_expr = re.sub(r'\\sin\^\{2\}\{.*?\\theta.*?\}', r'\\sin^2\\theta', latex_expr)
        latex_expr = latex_expr.replace(r'\sin{\left(\theta \right)}', r'\sin\theta')
        latex_expr = latex_expr.replace(r'\cos{\left(\theta \right)}', r'\cos\theta')
        latex_expr = re.sub(r'\\sin\{2\s*\\theta\s*\}', r'\\sin(2\\theta)', latex_expr)
        latex_expr = re.sub(r'\\sin\{\\left\(2\s*\\theta\s*\\right\)\}', r'\\sin(2\\theta)', latex_expr)
        
        # Fix tan to cot where appropriate
        latex_expr = re.sub(r'\\frac\{1\}\{.*?tan.*?\\theta.*?\}', r'\\cot\\theta', latex_expr)
        latex_expr = re.sub(r'\\frac\{1\}\{.*?\\tan.*?\\theta.*?\}', r'\\cot\\theta', latex_expr)
        # Remove specific stray closing braces (like }\} at end of cot\theta)
        latex_expr = re.sub(r'\\cot\\theta\}\}$', r'\\cot\\theta', latex_expr)
        
        # Clean up spacing
        latex_expr = re.sub(r'\s+', ' ', latex_expr)
        latex_expr = latex_expr.strip()
        
        print(f"{latex_name} = ${latex_expr}$\n")


def convert_to_readable_math():
    """
    Alternative: Converts to a more human-readable mathematical notation
    without full LaTeX.
    """
    print("Running step1.py and converting outputs to readable mathematical format...\n")
    print("=" * 70)
    
    # Read and execute step1.py while suppressing print statements
    try:
        # Read step1.py
        with open('step1.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Comment out all print statements
        lines = code.split('\n')
        modified_lines = []
        for line in lines:
            if 'print(' in line and not line.strip().startswith('#'):
                indent = len(line) - len(line.lstrip())
                modified_lines.append(' ' * indent + '# ' + line.lstrip())
            else:
                modified_lines.append(line)
        
        code = '\n'.join(modified_lines)
        
        # Execute the modified code
        namespace = {}
        exec(compile(code, 'step1.py', 'exec'), namespace)
        Γ = namespace['Gamma']
        
    except FileNotFoundError:
        print("Error: Could not find step1.py. Make sure it's in the same directory.")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing step1.py: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    symbols_to_print = [
        ((0, 0, 0), 'Γᵗₜₜ'),
        ((0, 0, 1), 'Γᵗₜᵣ'),
        ((0, 1, 1), 'Γᵗᵣᵣ'),
        ((1, 0, 0), 'Γʳₜₜ'),
        ((1, 0, 1), 'Γʳₜᵣ'),
        ((1, 1, 1), 'Γʳᵣᵣ'),
        ((2, 1, 2), 'Γᶿᵣθ'),
        ((1, 2, 2), 'Γʳθθ'),
        ((3, 1, 3), 'Γᵠᵣφ'),
        ((1, 3, 3), 'Γʳφφ'),
        ((2, 3, 3), 'Γᶿφφ'),
        ((3, 2, 3), 'Γᵠθφ'),
    ]
    
    print("Christoffel Symbols in readable format:\n")
    
    for indices, name in symbols_to_print:
        mu, nu, rho = indices
        expr = Γ[mu][nu][rho]
        
        # Convert to string and clean up
        expr_str = str(expr)
        
        # Replace function notation
        expr_str = expr_str.replace('alpha(t, r)', 'α')
        expr_str = expr_str.replace('beta(t, r)', 'β')
        
        # Replace Derivative notation
        expr_str = re.sub(r'Derivative\(alpha\(t, r\), t\)', '∂α/∂t', expr_str)
        expr_str = re.sub(r'Derivative\(alpha\(t, r\), r\)', '∂α/∂r', expr_str)
        expr_str = re.sub(r'Derivative\(beta\(t, r\), t\)', '∂β/∂t', expr_str)
        expr_str = re.sub(r'Derivative\(beta\(t, r\), r\)', '∂β/∂r', expr_str)
        
        # Replace exp
        expr_str = expr_str.replace('exp', 'e')
        
        # Replace sin, cos
        expr_str = expr_str.replace('sin(theta)', 'sin(θ)')
        expr_str = expr_str.replace('cos(theta)', 'cos(θ)')
        
        print(f"{name} = {expr_str}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--readable":
        convert_to_readable_math()
    else:
        convert_sympy_output_to_latex()
        print("\n" + "=" * 70)
        print("Tip: Use --readable flag for a more human-readable format")
        print("Example: python convert_to_latex.py --readable")
