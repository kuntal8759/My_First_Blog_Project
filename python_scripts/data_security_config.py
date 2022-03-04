# Import Required Modules.
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import bleach


class PasswordSecurity:
    """This class deals with securing the user password."""

    method = None
    salt = None
    hash_val = None

    def encrypt_password(self, pw: str) -> tuple:
        """Take password data as string and return hashed value of that password as string, but before that
        modifying the final output value in a certain way."""

        hashed_data = generate_password_hash(password=pw, method="pbkdf2:sha512:1048576", salt_length=32)
        self.method, self.salt, self.hash_val = hashed_data.split("$", 2)
        return self.salt, self.hash_val

    @staticmethod
    def decrypt_password(uuid, pwhash, password: str):
        """Take hashed password value & the password (that needed to be checked) as string and return
        True/False depending on the match."""

        pwhash = "pbkdf2:sha512:1048576" + "$" + uuid + "$" + pwhash
        return check_password_hash(pwhash=pwhash, password=password)


class DataSecurity:
    """This class deals with securing the email address of the user."""

    @staticmethod
    def data_hash(data: str) -> str:
        """Take input data as string and return hashed value of that data as string."""

        byte_data = data.encode()
        hashed_data = hashlib.sha512(byte_data).hexdigest()
        return hashed_data


class UserInputSecurity:
    """This class deals with the prevention of malicious script entered by the user."""

    @staticmethod
    def script_filter(content: str) -> str:
        """This function prevents the insertion of malicious python_scripts (Evil Scripts) in the database
        (by the user) by only allowing certain HTML tags & few attributes of some HTML tags, while
        blocking everything else."""

        allowed_tags = ['a', 'abbr', 'acronym', 'address', 'b', 'br', 'div', 'dl', 'dt',
                        'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img',
                        'li', 'ol', 'p', 'pre', 'q', 's', 'small', 'strike',
                        'span', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th',
                        'thead', 'tr', 'tt', 'u', 'ul', 'strong']

        allowed_attrs = {
            'a': ['href', 'target', 'title'],
            'img': ['src', 'alt', 'width', 'height'],
            "*": ["style"]
        }

        allowed_protocols = ["https"]

        # First Allow "style" Attribute For All HTML Tags (*) Before 👇👇 This Line.
        allowed_styles = ["font-family", "font-size", "text-align"]

        cleaned = bleach.clean(content,
                               tags=allowed_tags,
                               attributes=allowed_attrs,
                               styles=allowed_styles,
                               protocols=allowed_protocols,
                               strip=True)

        return cleaned
