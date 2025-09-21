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
import datetime
import uuid
import ast
import operator as op
from typing import Any, Dict, Union,List
# Operatori consentiti
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
    #The class handles any program errors
    def __init__(self,errorcode,errormessage):
        self.__errorcode = errorcode
        self.__errormessage = errormessage
        self.__error = False

    @property
    def error(self):
        return self.__error
    @error.setter
    def error(self,value):
        self.__error = value
    @error.deleter
    def error(self):
        del self.__error
    #----------------------------
    @property
    def errorcode(self):
        return self.__errorcode
    @errorcode.setter
    def errorcode(self,value):
        self.__errorcode = value
        self.__error = True
    @errorcode.deleter
    def errorcode(self):
        del self.__errorcode
    #----------------------------
    @property
    def errormessage(self):
        return self.__errormessage
    @errormessage.setter
    def errormessage(self,value):
        self.__errormessage = value
    @errormessage.deleter
    def errormessage(self):
        del self.__errormessage
#==========================================================
class utility_n4:
    #-------------------------------------------------------
    #utility Nios4
    def tid(self):
        #create tid (time id) using timezone 0
        val = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')
        #controllo che non mi finisca con un 60
        sval = str(int(val))
        if sval[-2:] == "60":
            val = val-1
        return int(val)
    #-------------------------------------------------------
    def gguid(self):
        return str(uuid.uuid4())
    #-------------------------------------------------------
    def convap(self,value):
        if value == None:
            return ""
        valore =str(value).replace("'", "''")
        return valore
    #-------------------------------------------------------
    def float_to_str(self,f):
        #convert float number to string
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

        # Numeri letterali: int/float
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Sono ammessi solo numeri (int/float) come costanti.")

        # Compatibilità Python <3.8 (se mai servisse)
        if hasattr(ast, "Num") and isinstance(node, getattr(ast, "Num")):  # type: ignore[attr-defined]
            return node.n  # type: ignore[attr-defined]

        # Variabili: ammesse solo se presenti nel dizionario
        if isinstance(node, ast.Name):
            if node.id in env:
                val = env[node.id]
                if not isinstance(val, (int, float)):
                    raise TypeError(f"Il valore di '{node.id}' deve essere numerico.")
                return val
            raise NameError(f"Variabile non definita: {node.id}")

        # Qualsiasi altra cosa (chiamate, attributi, ecc.) è vietata
        raise ValueError(f"Elemento dell'espressione non consentito: {type(node).__name__}")
    #-------------------------------------------------------
    def calc_expression(self,expr: str, values: Dict[str, Number]) -> Number:
        """
        Valuta in modo sicuro un'espressione matematica contenente variabili, numeri,
        operatori aritmetici (+,-,*,/,//,%,**), segni unari e parentesi.

        Args:
            expr: es. "prezzosingolo * quantitatotale"
            valori: es. {"prezzosingolo": 1, "quantitatotale": 20}

        Returns:
            int | float: il risultato calcolato

        Raises:
            NameError, TypeError, ValueError, ZeroDivisionError
        """
        # parsing in modalità 'eval' (solo un'espressione)
        tree = ast.parse(expr, mode="eval")
        return self._eval_node(self,tree.body, values)
    #-------------------------------------------------------
    def extract_expression_value(self,expr: str) -> List[str]:
        """
        Estrae i nomi delle variabili da un'espressione matematica.

        Args:
            expr (str): espressione, es. "prezzosingolo * quantitatotale"

        Returns:
            List[str]: lista di variabili distinte
        """
        tree = ast.parse(expr, mode="eval")
        variabili = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                variabili.append(node.id)

        # Rimuovo duplicati mantenendo l'ordine
        return list(dict.fromkeys(variabili))    
    #-------------------------------------------------------    