import _lexer,_parser
from _lexer import *
from _parser import *
from Crypto.Cipher import DES,DES3
import os
import binascii
import sys
import inspect
import rsa
from Crypto import Random
import hashlib
import serial
import msvcrt
current_line = 1  # 添加行号计数器
debug_mode = False
step_mode = "OVER"
bp_line_list = [107]
def get_key():
    """Wait for a keypress and return the key as a string."""
    key = msvcrt.getch()
    if key == b'\x00' or key == b'\xe0':
        # Handle special keys
        key = msvcrt.getch()
        if key == b'H':
            return 'up'
        elif key == b'P':
            return 'down'
        elif key == b'K':
            return 'left'
        elif key == b'M':
            return 'right'
        elif key == b'D':
            return 'F10'
        elif key == b'\x85':
            return 'F11'
        elif key == b'\x3f':
            return 'F5'
        else:
            return ''
    else:
        return key.decode('utf-8')
def cmd_debug_input():
    print("lineno:{}".format(current_line))
    while True:
        print("Press 'F5' key to continue run,'F10' key to step over,'F11' key to step in: ")
        user_input = get_key()
        if user_input == 'F10':
            step_mode = "OVER"
            break
        elif user_input == 'F11':
            step_mode = "IN"
            break
        elif user_input == 'F5':
            step_mode = "RUN"
            break 
class ReturnValueException(Exception):
    def __init__(self, value):
        self.value = value
class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        if debug_mode and  type(node).__name__ in ['String', 'HexStr', 'Num', 'Bool', 'Var', 'HexStrArray']:
            if node.lineno != current_line:
                if step_mode == "RUN" and node.lineno not in bp_line_list:
                    pass
                elif self.step_over_function == True and step_mode == "OVER" and node.lineno != current_line + 1 and node.lineno not in bp_line_list:
                    pass
                else:
                    self.step_over_function = False
                    current_line = node.lineno
                    cmd_debug_input()               
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))
class Interpreter(NodeVisitor):
    def __init__(self,parser):
        self.parser = parser
        self.GLOBAL_SCOPE = {}
        self.log=''
        self.break_loop=False
        self.continue_loop=False
        self.step_over_function = False
        self.custom_functions = []
        self.system_functions = ['print','exit','send', 'itoa','atoi','totlv','len',
                                 'load_file',
                                 'des_encrypt_ecb','des_decrypt_ecb','des_encrypt_cbc','des_decrypt_cbc','des_mac',
                                 'rsa_enc','rsa_dec','rsa_sign','rsa_verify']  # add more functions as needed

    def visit_StatementList(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_IfStatement(self, node):
        if self.visit(node.condition):
            self.visit(node.if_body)
        elif node.else_body:
            self.visit(node.else_body)

    def visit_ForStatement(self, node):
        self.visit(node.init)
        while self.visit(node.condition):
            if isinstance(node.body, StatementList):
                for statement in node.body.statements:
                    self.visit(statement)
                    if self.continue_loop:  # check for continue statement
                        self.continue_loop=False
                        break
                    if self.break_loop:  # check for break statement
                        break
            else:
                self.visit(node.body)
                if self.continue_loop:  # check for continue statement
                    self.continue_loop = False
                    break
                if self.break_loop:  # check for break statement
                    break
            if self.break_loop:  # check for break statement
                self.break_loop = False
                break
            self.visit(node.update)

    def visit_WhileStatement(self, node):
        while self.visit(node.condition):
            if isinstance(node.body, StatementList):
                for statement in node.body.statements:
                    self.visit(statement)
                    if self.continue_loop:  # check for continue statement
                        self.continue_loop=False
                        break
                    if self.break_loop:  # check for break statement
                        break
            else:
                self.visit(node.body)
                if self.continue_loop:  # check for continue statement
                    self.continue_loop = False
                    break
                if self.break_loop:  # check for break statement
                    break
            if self.break_loop:  # check for break statement
                self.break_loop = False
                break

    def visit_DoWhileStatement(self, node):
        while True:
            if isinstance(node.body, StatementList):
                for statement in node.body.statements:
                    self.visit(statement)
                    if self.continue_loop:
                        self.continue_loop = False
                        break
                    if self.break_loop:
                        self.break_loop = False
                        return
            else:
                self.visit(node.body)
                if self.continue_loop:
                    self.continue_loop = False
                    break
                if self.break_loop:
                    self.break_loop = False
                    return
            if not self.visit(node.condition):
                break
    def visit_BreakStatement(self, node):
        self.break_loop = True

    def visit_ContinueStatement(self, node):
        self.continue_loop = True  # set continue_loop to True

    def visit_SwitchStatement(self, node):
        condition = self.visit(node.condition)
        hit = False
        for i,case in enumerate(node.cases):
            case_value = self.visit(case[0])
            if condition == case_value:
                hit = True
                self.visit(case[1])
                if self.break_loop:
                    break
                else:
                    if i < len(node.cases) - 1:
                        next_case = node.cases[i+1]
                        condition = self.visit(next_case[0])
                    else:
                        break
        if (self.break_loop == False or hit == False) and node.default_case:
            self.visit(node.default_case)
        if self.break_loop:
            self.break_loop = False

    def visit_str(self, node):
        return node
    def visit_String(self,node):
        return node.value
    def visit_HexStr(self,node):
        return node.value
    def visit_NoneType(self,node):
        return ''
    def visit_Num(self, node):
        return int(node.value)
    def visit_Bool(self,node):
        if node.value == 'true':
            return True
        else:
            return False
    def visit_BinOp(self, node):
        if node.op.type == PLUSASSIGN:
            self.GLOBAL_SCOPE[node.left.value] += self.visit(node.right)
            return self.GLOBAL_SCOPE[node.left.value]
        elif node.op.type == MINUSASSIGN:
            self.GLOBAL_SCOPE[node.left.value] -= self.visit(node.right)
            return self.GLOBAL_SCOPE[node.left.value]
        elif node.op.type == MULASSIGN:
            self.GLOBAL_SCOPE[node.left.value] *= self.visit(node.right)
            return self.GLOBAL_SCOPE[node.left.value]
        elif node.op.type == DIVASSIGN:
            self.GLOBAL_SCOPE[node.left.value] /= (int)(self.visit(node.right))
            return self.GLOBAL_SCOPE[node.left.value]
        elif node.op.type == MODASSIGN:
            self.GLOBAL_SCOPE[node.left.value] %= (int)(self.visit(node.right))
            return self.GLOBAL_SCOPE[node.left.value]
        elif node.op.type in (PLUS, MINUS,MUL,DIV,MOD,EQ,NE,LT,GT,LE,GE,OR,AND,BOR,BXOR,BAND,SHIFTLEFT,SHIFTRIGHT):
            left = self.visit(node.left)
            right = self.visit(node.right)
            if isinstance(left,int):
                if isinstance(right,Bool):
                    if node.op.type == OR:
                        return left or right
                    elif node.op.type == AND:
                        return left and right
                elif isinstance(right,int):
                    if node.op.type == PLUS:
                        return left + right
                    elif node.op.type == MINUS:
                        return left - right
                    elif node.op.type == MUL:
                        return left * right
                    elif node.op.type == DIV:
                        if right == 0:
                            Exception("cannot be divided by zero!")
                        return (int)(left / right)
                    elif node.op.type == MOD:
                        if right == 0:
                            Exception("cannot get mode by zero!")
                        return (int)(left % right)
                    elif node.op.type == EQ:
                        return left == right
                    elif node.op.type == NE:
                        return left != right
                    elif node.op.type == LT:
                        return int(left) < int(right)
                    elif node.op.type == GT:
                        return int(left) > int(right)
                    elif node.op.type == LE:
                        return int(left) <= int(right)
                    elif node.op.type == GE:
                        return int(left) >= int(right)
                    elif node.op.type == OR:
                        return left or right
                    elif node.op.type == AND:
                        return left and right
                    elif node.op.type == BOR:
                        return left | right
                    elif node.op.type == BXOR:
                        return left ^ right
                    elif node.op.type == BAND:
                        return left & right
                    elif node.op.type == SHIFTLEFT:
                        return left << right
                    elif node.op.type == SHIFTRIGHT:
                        return left >> right
                    else:
                        raise Exception("left type:INTEGER cannot do operation({}) with right type:INTEGER".format(node.op.type))
                else:
                    raise Exception("left type:INTEGER not equal right type:STRING")
            else:
                if isinstance(left,Bool):
                    if node.op.type == OR:
                        return left or right
                    elif node.op.type == AND:
                        return left and right
                elif (isinstance(left,HexStr) or isinstance(left,str)) and (isinstance(right,HexStr) or isinstance(right,str)):
                    if node.op.type == PLUS:
                        return str(left) + str(right)
                    elif node.op.type == EQ:
                        return str(left) == str(right)
                    elif node.op.type == NE:
                        return str(left) != str(right)
                    else:
                        raise Exception("left type:STRING cannot do operation({}) with right type:STRING".format(node.op.type))
                elif (isinstance(left,HexStr) or isinstance(left,str)) and isinstance(right,int):
                    if node.op.type == MUL:
                        return str(left) * right
                    elif node.op.type == SHIFTLEFT:
                        return str(left)[right * 2:]
                    elif node.op.type == SHIFTRIGHT:
                        return str(left)[:-right * 2]
                else:
                    raise Exception("left type:STRING not equal right type:INTEGER")
        return node.value
    def visit_UnaryOp(self, node):
        if node.op.type == NOT:
            return not self.visit(node.expr)
        elif node.op.type == BNOT:
            return ~self.visit(node.expr)
        elif node.op.type == PPP:
            self.GLOBAL_SCOPE[node.expr.token.value] = self.GLOBAL_SCOPE[node.expr.token.value] + 1
            return self.GLOBAL_SCOPE[node.expr.token.value]
        elif node.op.type == PPS:
            value = self.GLOBAL_SCOPE[node.expr.token.value]
            self.GLOBAL_SCOPE[node.expr.token.value] = self.GLOBAL_SCOPE[node.expr.token.value] + 1
            return value
        elif node.op.type == MMP:
            self.GLOBAL_SCOPE[node.expr.token.value] = self.GLOBAL_SCOPE[node.expr.token.value] - 1
            return self.GLOBAL_SCOPE[node.expr.token.value]
        elif node.op.type == MMS:
            value = self.GLOBAL_SCOPE[node.expr.token.value]
            self.GLOBAL_SCOPE[node.expr.token.value] = self.GLOBAL_SCOPE[node.expr.token.value] - 1
            return value
        else:
            raise Exception('Unknown operator: {}'.format(op))
    def visit_Var(self, node):
        var_name = node.value
        if var_name in self.GLOBAL_SCOPE:
            return self.GLOBAL_SCOPE[var_name]
        else:
            if re.match(r'[0-9a-fA-F]', var_name) and len(var_name) % 2 == 0:
                node.token = HEXSTR
                return var_name
            else:
                raise NameError(repr(var_name))

    def visit_HexStrArray(self, node):
        value = self.GLOBAL_SCOPE.get(node.token.value)
        strValue = str(value)
        if node.start is None:
            start = 0
        else:
            start = int(self.visit(node.start)) * 2
        if node.end is None:
            end = len(strValue)
        else:
            end = int(self.visit(node.end)) * 2
        if node.colon:
            return strValue[start : end]
        else:
            if start >= 0:
                return strValue[start : start + 2]
            else:
                return strValue[len(strValue) + start : len(strValue) + start + 2]

    def visit_Assign(self, node):
        if isinstance(node.left,HexStrArray):
            right = node.right
            node = node.left
            value = self.GLOBAL_SCOPE.get(node.token.value)
            strValue = str(value)
            if node.start is None:
                start = 0
            else:
                start = int(self.visit(node.start)) * 2
            if node.end is None:
                end = len(strValue)
            else:
                end = int(self.visit(node.end)) * 2
            if node.colon == False:
                if start >= 0:
                    end = start + 2
                else:
                    start = len(strValue) + start
                    end = len(strValue) + start + 2
            var_name = node.token.value
            newValue = self.visit(right)
            self.GLOBAL_SCOPE[var_name] = value[:start]+newValue+value[end:]
            return newValue
        else:
            var_name = node.left.value
            self.GLOBAL_SCOPE[var_name] = self.visit(node.right)
            return self.GLOBAL_SCOPE[var_name]

    def visit_FuncDef(self, node):
        self.custom_functions.append(node)

    def visit_ReturnStatement(self, node):
        value = self.visit(node.value)
        raise ReturnValueException(value)

    def visit_FuncCall(self, node):
        func_name = node.name
        args = [self.visit(arg) for arg in node.args]
        if func_name in self.system_functions:
            return getattr(self, 'system_{}'.format(func_name))(args)
        else:
            find = False
            for node in self.custom_functions:
                if node.name == func_name:
                    func_def = node
                    len_args = len(args)
                    for i, arg in enumerate(func_def.args):
                        if i >= len_args:
                            default_value = func_def.defaults.get(arg, None)
                            if default_value is not None:
                                args.append(self.visit(default_value))
                    if len(args) != len(func_def.args):
                        raise Exception("Expected {} arguments, but got {}".format(len(func_def.args), len(args)))
                    local_scope = {}
                    new_GLOBAL_SCOPE0={}
                    for arg_name, arg_value in zip(func_def.args, args):
                        local_scope[arg_name] = arg_value
                    for key in local_scope.keys():
                        if key in self.GLOBAL_SCOPE.keys():
                            value = self.GLOBAL_SCOPE[key]
                            del self.GLOBAL_SCOPE[key]
                            new_GLOBAL_SCOPE0[key] = value

                    self.GLOBAL_SCOPE.update(local_scope)
                    new_GLOBAL_SCOPE1 = self.GLOBAL_SCOPE.copy()
                    try:
                        self.step_over_function = True
                        self.visit(func_def.body)
                        self.step_over_function = False
                        new_GLOBAL_SCOPE2 = {k: v for k, v in self.GLOBAL_SCOPE.items() if k not in new_GLOBAL_SCOPE1}
                        new_GLOBAL_SCOPE3 = {k: v for k, v in self.GLOBAL_SCOPE.items() if k not in new_GLOBAL_SCOPE2 and k not in local_scope}
                        self.GLOBAL_SCOPE = new_GLOBAL_SCOPE3
                        self.GLOBAL_SCOPE.update(new_GLOBAL_SCOPE0)
                        find = True
                    except ReturnValueException as e:
                        return e.value
                    break
            if not find :
                raise Exception("No definition found for function {}".format(func_name))

    def interpret(self):
        tree = self.parser.parse()
        self.visit(tree)
    def system_print(self, args):
        values = [arg for arg in args]
        print(*values)

    def system_exit(self, args):
        sys.exit()

    def system_send(self, args):
        cmd = args[0]
        self.log += ">>" + str(cmd) + '\r\n'
        '''try:
            ser = serial.Serial('COM1', 115200)
        except serial.SerialException as e:
        # process Serial Connection Error
            self.log += "Serial Connection Error: " + str(e) + '\r\n'
            return None
        try:
            ser.write(cmd.encode())
            data = ser.readline().decode().strip()
        except serial.SerialException as e:
        # process Serial Communication Error
            self.log += "Serial Communication Error: " + str(e) + '\r\n'
            return None'''
        #send and receive data simulator
        data='9000'
        if cmd == '8050000008b95c2b8c2e671007':
            data = '00000000000000000000ff020000db307f752329265a5cf74aaf949d'
        elif cmd == '8482000010d246f86de1fbb36e9813dc9281ca011d':
            data = '9000'
        elif cmd == '80E60c002907a000000151535008a00000015153504105112233444401800ec90481020255ef06cf0141cf014200':
            data = '009000'
        self.log += "<<" + str(data) + '\r\n'
        return data
    def system_totlv(self,args):
        tag = args[0]
        value = args[1]
        length = (len(str(value)) >> 1)
        return tag + hex(length)[2:].zfill(2) + value

    def system_len(self,args):
        value = args[0]
        return int(len(str(value))/2)
    def system_atoi(self,args):
        hex_str = args[0]
        if len(hex_str) != 2:
            raise ValueError("Incorrect ascii length")
        return int(hex_str, 16)
    def system_itoa(self,args):
        dec_value = args[0]
        if int(dec_value) > 65535:
            raise ValueError("Incorrect decimal length")
        if int(dec_value) > 255:
            return hex(int(dec_value))[2:].lower().zfill(4)
        else:
            return hex(int(dec_value))[2:].lower().zfill(2)
    def system_load_file(self,args):
        path = args[0]
        try:
            with open(path, 'rb') as f:
                binary_data = f.read()
        except FileNotFoundError:
            raise ValueError("File not found")
        if path[-3:] =='cap':
            cap_data = binary_data[0:0]
            for cap_type in [b"Header.cap", b"Directory.cap", b"Import.cap",b"Applet.cap",b"Class.cap",b"Method.cap",b"StaticField.cap",b"Export.cap",b"ConstantPool.cap",b"RefLocation.cap"]:
                cap_pos = binary_data.find(cap_type)
                if cap_pos != -1:
                    cap_pos += len(cap_type)
                    length = int.from_bytes(binary_data[cap_pos + 1:cap_pos + 3], byteorder="big")
                    cap_data += binary_data[cap_pos:cap_pos + 3 + length]
            return binascii.hexlify(cap_data).decode()
        elif path[-3:] =='elf':
            return binascii.hexlify(binary_data).decode()
    def system_des_encrypt_cbc(self,args):
        iv = binascii.unhexlify(args[0].encode())
        plaintext = binascii.unhexlify(args[1].encode())
        key = binascii.unhexlify(args[2].encode())
        if len(key) != 16:
            raise ValueError("Incorrect DES key length")
        cipher = DES3.new(key, DES3.MODE_CBC, iv)
        ciphertext = binascii.hexlify(cipher.encrypt(plaintext)).decode()
        return ciphertext

    def system_des_encrypt_ecb(self,args):
        plaintext = binascii.unhexlify(args[0].encode())
        key = binascii.unhexlify(args[1].encode())
        if len(key) != 16:
            raise ValueError("Incorrect DES key length")
        cipher = DES3.new(key, DES3.MODE_ECB)
        ciphertext = binascii.hexlify(cipher.encrypt(plaintext)).decode()
        return ciphertext

    def system_des_decrypt_cbc(self,args):
        iv = binascii.unhexlify(args[0].encode())
        ciphertext = binascii.unhexlify(args[1].encode())
        key = binascii.unhexlify(args[2].encode())
        if len(key) != 16:
            raise ValueError("Incorrect DES key length")
        cipher = DES3.new(key, DES3.MODE_CBC,iv)
        plaintext = binascii.hexlify(cipher.decrypt(ciphertext)).decode()
        return plaintext
    def system_des_decrypt_ecb(self,args):
        ciphertext = binascii.unhexlify(args[0].encode())
        key = binascii.unhexlify(args[1].encode())
        if len(key) != 16:
            raise ValueError("Incorrect DES key length")
        cipher = DES3.new(key, DES3.MODE_ECB)
        plaintext = binascii.hexlify(cipher.decrypt(ciphertext)).decode()
        return plaintext
    def system_des_mac(self,args):
        iv = binascii.unhexlify(args[0].encode())
        text = binascii.unhexlify(args[1].encode())
        key = binascii.unhexlify(args[2].encode())
        if len(key) != 16:
            raise ValueError("Incorrect DES key length")
        key1 = key[:8]
        text += b'\x80'
        while len(text) % 8 != 0:
            text += b'\x00'
        txtlen = len(text) - 8
        for i in range(0,txtlen,8):
            cipher = DES.new(key1, DES.MODE_CBC, iv)
            iv = cipher.encrypt(text[i:i + 8])
        cipher = DES3.new(key, DES3.MODE_CBC, iv)
        mac = binascii.hexlify(cipher.encrypt(text[-8:])).decode()
        return mac
    def system_rsa_enc(self,args):
        plainTxt = args[0]
        public_key_n = args[1]
        public_key_e = args[2]
        pubkey = rsa.PublicKey(
            int(public_key_n,16),
            int(public_key_e,16),
        )
        plainTxt = binascii.unhexlify(plainTxt.encode())
        ciphertext = rsa.encrypt(plainTxt, pubkey)
        return binascii.hexlify(ciphertext).decode()
    def system_rsa_dec(self,args):
        cipherTxt = args[0]
        public_key_n = args[1]    
        public_key_e = args[2]    
        private_key_d = args[3]
        private_key_p = args[4]    
        private_key_q = args[5]
        prikey = rsa.PrivateKey(
            int(public_key_n,16),
            int(public_key_e,16),
            int(private_key_d,16),
            int(private_key_p,16),
            int(private_key_q,16)
        )
        cipherTxt = binascii.unhexlify(cipherTxt.encode())
        plainTxt = rsa.decrypt(cipherTxt, prikey)
        return binascii.hexlify(plainTxt).decode()
        
    def system_rsa_sign(self,args):
        message = args[0]
        publicKeyN = args[1]
        publicKeyE = args[2]
        privateKeyD = args[3]
        privateKeyP = args[4]
        privateKeyQ = args[5]
        # Generate a SHA-256 digest of the message
        message = binascii.unhexlify(message.encode())
        if len(publicKeyN) / 2 == 128:
            digest = hashlib.sha1(message).digest()
        else:
            digest = hashlib.sha256(message).digest()

        # Sign the digest with the private key
        prikey = rsa.PrivateKey(
            int(publicKeyN, 16),
            int(publicKeyE, 16),
            int(privateKeyD, 16),
            int(privateKeyP, 16),
            int(privateKeyQ, 16),
        )
        if len(publicKeyN) / 2 == 128:
            signature = rsa.sign(digest, prikey, 'SHA-1')
        else:
            signature = rsa.sign(digest, prikey, 'SHA-256')

        # Return the signature as a hex string
        return binascii.hexlify(signature).decode()

    def system_rsa_verify(self,args):
        message = args[0]
        signature = args[1]
        publicKeyN = args[2]
        publicKeyE = args[3]
        # Generate a SHA-256 digest of the message
        message = binascii.unhexlify(message.encode())
        digest = hashlib.sha1(message).digest()

        # Verify the signature with the public key
        pubkey = rsa.PublicKey(
            int(publicKeyN, 16),
            int(publicKeyE, 16)
        )
        signature = binascii.unhexlify(signature.encode())
        verified = rsa.verify(digest, signature, pubkey)

        # Return True if the signature is valid, False otherwise
        return verified

with open('script.txt', 'r') as f:
    text = f.read()
lexer = Lexer(text)
parser = Parser(lexer)
interpreter = Interpreter(parser)
debug_mode = True
if debug_mode:
    cmd_debug_input()
interpreter.interpret()
print(interpreter.log)

