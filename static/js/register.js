/**
 * Created by lz on 2015/12/19.
 */
$(document).ready(function () {
	$('#user-name-label').hide();

	$('#user-info-form').validate({
		rules: {
			username: "required",
			email: {
				required: true,
				email: true
			},
			password: {
				required: true,
				minlength: 6
			},
			confirmPassword: {
				required: true,
				equalTo: "#password"
			}
		}
	});


	$('#username').bind('blur', function(){
		name = $("#username").val();
		$.get("/validateUserName/", {'userName':name}, function(ret){
			$('#user-name-label').text('Someone already has that username. Try another?');
			if (ret == "no"){
				$('#user-name-label').show();
			}
			else{
				$('#user-name-label').hide();
			}
		})
	});
});
