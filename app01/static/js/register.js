// function checkPasswords() {
//             var password1 = document.getElementById("password1").value;
//             var password2 = document.getElementById("password2").value;
//             var errorElement = document.getElementById("passwordError");
//
//             if (password1 !== password2) {
//                 errorElement.textContent = "Passwords do not match.";
//                 return false; // Prevent form submission
//             } else {
//                 errorElement.textContent = ""; // Clear the error message
//                 return true; // Allow form submission
//             }
//         }

        function validateField(field, errorElement, validationFunction) {
            if (!validationFunction(field.value)) {
                errorElement.textContent = validationFunction.errorMessage;
                return false;
            } else {
                errorElement.textContent = "";
                return true;
            }
        }

        // Validation functions
        function validateUsername(username) {
            var regex = /^[A-Za-z0-9@.\/+\-_]+$/;
            if (username.length > 150) {
                validateUsername.errorMessage = "Username must be 150 characters or fewer.";
                return false;
            }
            if(username.length == 0) {
                validateUsername.errorMessage = "Username cannot be empty.";
                return false;
            }
            if (!regex.test(username)) {
                validateUsername.errorMessage = "Username can only contain letters, digits and @/./+/-/_ characters.";
                return false;
            }
            return true;
        }

        function validateEmail(email) {
            var regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            validateEmail.errorMessage = "Enter a valid email address.";
            return regex.test(email);
        }

        function validatePassword(password) {
            if (password.length < 8) {
                validatePassword.errorMessage = "Password must contain at least 8 characters.";
                return false;
            }
            if (/^\d+$/.test(password)) {
                validatePassword.errorMessage = "Password can't be entirely numeric.";
                return false;
            }
            return true;
        }

        document.getElementById("username").addEventListener("blur", function() {
            validateField(this, document.getElementById("usernameError"), validateUsername);
        });

        document.getElementById("email").addEventListener("blur", function() {
            validateField(this, document.getElementById("emailError"), validateEmail);
        });

        document.getElementById("password1").addEventListener("blur", function() {
            validateField(this, document.getElementById("password1Error"), validatePassword);
             var password1 = document.getElementById("password1").value;
            var password2 = this.value;
            var errorElement = document.getElementById("password2Error");

            if (password1 !== password2) {
                errorElement.textContent = "Passwords do not match.";
            } else {
                errorElement.textContent = "";
            }
        });

        document.getElementById("password2").addEventListener("blur", function() {
            var password1 = document.getElementById("password1").value;
            var password2 = this.value;
            var errorElement = document.getElementById("password2Error");

            if (password1 !== password2) {
                errorElement.textContent = "Passwords do not match.";
            } else {
                errorElement.textContent = "";
            }
        });

        document.getElementById("registerForm").addEventListener("submit", function(event) {
            var usernameValid = validateField(document.getElementById("username"), document.getElementById("usernameError"), validateUsername);
            var emailValid = validateField(document.getElementById("email"), document.getElementById("emailError"), validateEmail);
            var password1Valid = validateField(document.getElementById("password1"), document.getElementById("password1Error"), validatePassword);
            var passwordsMatch = checkPasswords();

            if (!usernameValid || !emailValid || !password1Valid || !passwordsMatch) {
                return false; // 阻止默认的提交行为
            }
        });

        // 在页面加载完成后执行
        window.onload = function() {
            // 获取所有具有 "error" 类的元素
            var errorElements = document.querySelectorAll('.error');

            // 遍历所有错误元素
            errorElements.forEach(function(element) {
                // 设置一个定时器，在5秒后隐藏错误消息
                setTimeout(function() {
                    element.style.display = 'none'; // 隐藏错误消息
                }, 5000); // 5000毫秒即5秒
            });
        };
