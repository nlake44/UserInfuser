jQuery(function() {
	$("#submit")
			.click(
					function() {
						$(".error").hide();
						var hasError = false;
						var passwordVal = $("#password").val();
						var checkVal = $("#password_repeat").val();
						if (passwordVal == '') {
							$("#submit")
									.after(
											'<br/><span class="error">Please enter a password.</span>');
							hasError = true;
						} else if (checkVal == '') {
							$("#submit")
									.after(
											'<br/><span class="error">Please re-enter your password.</span>');
							hasError = true;
						} else if (passwordVal != checkVal) {
							$("#submit")
									.after(
											'<br/><span class="error">Passwords do not match.</span>');
							hasError = true;
						}
						if (hasError == true) {
							return false;
						}
					});
});