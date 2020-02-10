 	document.getElementById('login-form').addEventListener('submit',function(e){
	e.preventDefault();
	
	//const formdata1 = new FormData();
	let data1= new FormData();
    const name2 = document.getElementById('your_email').value;
    const code = document.getElementById('code').value;
    const pass =document.getElementById('your_pass').value;


    //const name1=document.getElementById('your_pass').value;
    const api_key="a93e8f09748d43f3a44571f2893d5c2b";
    const client_id="6329761b61bf4e569217c946fc3c0392";
    //const token = localStorage.getItem('user_login_token');
    reset_password(api_key,client_id,code,name2,pass);
                    
	
});


function reset_password(api_key,client_id,code,name,pass){  
    var json_data_user_email_verify = {
        "api_key":api_key,
		"client_id":client_id,
        "email":name2 ,
        "code":code,
        "password":pass
    };

var data_user_reset_password = JSON.stringify(json_data_user_email_verify);
console.log(data_user_reset_password);
    //showLoader();
xhr = new XMLHttpRequest();
var url = "http://52.203.240.40:8080/user/reset_password";

xhr.open("POST", url, true);
xhr.setRequestHeader("Content-type", "application/json");

//xhr.setRequestHeader('Access-Control-Allow-Origin','*');
xhr.onreadystatechange = function () { 
    if (xhr.readyState == 4 && xhr.status >= 200) {
        var json = JSON.parse(xhr.responseText);
        console.log(json);
     if(xhr.status==200){
     alert("SUCCESS")
        window.location="./USER_LOGIN.html";
}
else if (xhr.status>=400){
    console.log("error");
}
}  
}
xhr.send(data_user_reset_password);
}



