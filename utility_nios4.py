#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#================================================================================
#Copyright of Davide Sbreviglieri 2020
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
#================================================================================
#UTILITY NIOS4
#================================================================================
from __future__ import annotations

import datetime
import uuid
import ast
import operator as op
from typing import Any, Dict, List, Optional, Union

# Allowed operators
_BIN_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
}
_UNARY_OPS = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}

Number = Union[int, float]
#================================================================================
class error_n4:
    """
    Lightweight error container for Nios4 utilities.

    Stores an error code/message and a boolean flag indicating
    whether an error is currently present.
    """
    def __init__(self, errorcode: str, errormessage: str) -> None:
        """
        Initialize the error container.

        Parameters
        ----------
        errorcode : str
            Initial error code.
        errormessage : str
            Initial error message.
        """        
        self.__errorcode = errorcode
        self.__errormessage = errormessage
        self.__error = False

    @property
    def error(self) -> bool:
        """
        Error flag.

        Returns
        -------
        bool
            ``True`` if an error is present, ``False`` otherwise.
        """
        return self.__error
    
    @error.setter
    def error(self, value: bool) -> None:
        """
        Set the error flag.

        Parameters
        ----------
        value : bool
            New flag value.
        """
        self.__error = value

    @error.deleter
    def error(self) -> None:
        """Delete the error flag."""
        del self.__error

    # ----------------------------
    @property
    def errorcode(self) -> str:
        """
        Error code.

        Returns
        -------
        str
            Current error code.
        """
        return self.__errorcode
    
    @errorcode.setter
    def errorcode(self, value: str) -> None:
        """
        Set the error code and mark the container as errored.

        Parameters
        ----------
        value : str
            New error code.
        """
        self.__errorcode = value
        self.__error = True

    @errorcode.deleter
    def errorcode(self) -> None:
        """Delete the error code."""
        del self.__errorcode
    #----------------------------
    @property
    def errormessage(self) -> str:
        """
        Error message.

        Returns
        -------
        str
            Current error message.
        """
        return self.__errormessage
    
    @errormessage.setter
    def errormessage(self, value: str) -> None:
        """
        Set the error message.

        Parameters
        ----------
        value : str
            New error message.
        """
        self.__errormessage = value

    @errormessage.deleter
    def errormessage(self) -> None:
        """Delete the error message."""
        del self.__errormessage
#==========================================================
class utility_n4:
    """
    Miscellaneous Nios4 utility functions.

    Provides time-based identifiers, GUID generation, string helpers,
    and a safe arithmetic expression evaluator.
    """

    # -------------------------------------------------------
    def tid(self) -> int:
        """
        Create a TID (time-based integer id) in UTC.

        Returns
        -------
        int
            An integer timestamp formatted as ``YYYYMMDDHHMMSS`` in UTC.

        Notes
        -----
        Some systems may transiently produce a trailing ``...60`` for seconds;
        this method guards against that by decrementing the integer by 1
        if the last two digits are ``60``.
        """
        val = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')
        #controllo che non mi finisca con un 60
        sval = str(int(val))
        if sval[-2:] == "60":
            val = val-1
        return int(val)
    #-------------------------------------------------------
    def gguid(self) -> str:
        """
        Generate a new GUID (UUID4) as string.

        Returns
        -------
        str
            A freshly generated UUID4 string.
        """        
        return str(uuid.uuid4())
    #-------------------------------------------------------
    def convap(self, value: Optional[Any]) -> str:
        """
        Convert a Python value to a SQL-safe string.

        Parameters
        ----------
        value : Any or None
            Value to convert.

        Returns
        -------
        str
            Empty string for ``None``; otherwise the string with single quotes
            doubled (``'`` → ``''``).
        """
        if value == None:
            return ""
        valore =str(value).replace("'", "''")
        return valore
    #-------------------------------------------------------
    def float_to_str(self, f: Number) -> str:
        """
        Convert a numeric value to a non-scientific string representation.

        Parameters
        ----------
        f : int or float
            Numeric value to render.

        Returns
        -------
        str
            A string representation without scientific notation (e.g. ``1e-06``).

        Notes
        -----
        - For scientific notation, digits and exponent are expanded to a
          plain decimal representation.
        - Removes Python 2-style ``'L'`` suffixes if present in legacy data.
        """
        float_string = repr(f)
        if 'e' in float_string:  # detect scientific notation
            digits, exp = float_string.split('e')
            digits = digits.replace('.', '').replace('-', '')
            exp = int(exp)
            zero_padding = '0' * (abs(int(exp)) - 1)  # minus 1 for decimal point in the sci notation
            sign = '-' if f < 0 else ''
            if exp > 0:
                float_string = '{}{}{}.0'.format(sign, digits, zero_padding)
            else:
                float_string = '{}0.{}{}'.format(sign, zero_padding, digits)

        float_string = float_string.replace("L","")        

        return float_string
    #-------------------------------------------------------
    def _eval_node(self,node: ast.AST, env: Dict[str, Number]) -> Number:
        """
        Recursively evaluate an AST node for a numeric expression.

        Parameters
        ----------
        node : ast.AST
            The AST node to evaluate (from an ``ast.parse(..., mode='eval')`` tree).
        env : dict[str, int | float]
            Mapping of variable names to numeric values.

        Returns
        -------
        int or float
            The evaluated numeric result.

        Raises
        ------
        ValueError
            If the node or operator is not allowed, or non-numeric constants are used.
        NameError
            If a variable is referenced that is not provided in ``env``.
        TypeError
            If a provided variable value is non-numeric.
        ZeroDivisionError
            If a division by zero occurs during evaluation.
        """        
        if isinstance(node, ast.BinOp):
            left = self._eval_node(self,node.left, env)
            right = self._eval_node(self,node.right, env)
            op_type = type(node.op)
            if op_type not in _BIN_OPS:
                raise ValueError(f"Operatore non consentito: {op_type.__name__}")
            return _BIN_OPS[op_type](left, right)

        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(self,node.operand, env)
            op_type = type(node.op)
            if op_type not in _UNARY_OPS:
                raise ValueError(f"Operatore unario non consentito: {op_type.__name__}")
            return _UNARY_OPS[op_type](operand)

        # Numeric literals
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Sono ammessi solo numeri (int/float) come costanti.")

        # Python <3.8 compatibility (if ever needed)
        if hasattr(ast, "Num") and isinstance(node, getattr(ast, "Num")):  # type: ignore[attr-defined]
            return node.n  # type: ignore[attr-defined]

        # Variables must come from the environment
        if isinstance(node, ast.Name):
            if node.id in env:
                val = env[node.id]
                if not isinstance(val, (int, float)):
                    raise TypeError(f"Il valore di '{node.id}' deve essere numerico.")
                return val
            raise NameError(f"Variabile non definita: {node.id}")

        # Anything else (calls, attributes, subscripts, etc.) is forbidden
        raise ValueError(f"Elemento dell'espressione non consentito: {type(node).__name__}")
    #-------------------------------------------------------
    def calc_expression(self,expr: str, values: Dict[str, Number]) -> Number:
        """
        Safely evaluate a mathematical expression with variables.

        Parameters
        ----------
        expr : str
            The expression to evaluate (e.g., ``"unit_price * quantity"``).
        values : dict[str, int | float]
            Variable environment (e.g., ``{"unit_price": 1.5, "quantity": 20}``).

        Returns
        -------
        int or float
            The computed result.

        Raises
        ------
        NameError
            If an unknown variable name is used.
        TypeError
            If a variable value is non-numeric.
        ValueError
            If the expression contains disallowed elements/operators or constants.
        ZeroDivisionError
            If a division by zero occurs.
        """
        tree = ast.parse(expr, mode="eval")
        return self._eval_node(self,tree.body, values)
    #-------------------------------------------------------
    def extract_expression_value(self,expr: str) -> List[str]:
        """
        Extract distinct variable names from a mathematical expression.

        Parameters
        ----------
        expr : str
            The expression (e.g., ``"unit_price * quantity"``).

        Returns
        -------
        list of str
            Variable names in first-seen order (duplicates removed).
        """
        tree = ast.parse(expr, mode="eval")
        variables = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                variables.append(node.id)

        # Deduplicate preserving order
        return list(dict.fromkeys(variables))    
    #-------------------------------------------------------    