document.getElementById('register-form').addEventListener('submit',function(e){
	e.preventDefault();
	
	//const formdata1 = new FormData();
	let data1= new FormData();
    const name2 = document.getElementById('email').value;
    const name1=document.getElementById('name').value;
    const password2 = document.getElementById('pass').value;
    const api_key="74d9c3f6bb384d168b658069e3c1825a";
	const client_id="8ab95867280c41cdbfe1cfb9db7d16db";
	

    window.localStorage.setItem('api_key',api_key);
    window.localStorage.setItem('client_id',client_id);
   window.localStorage.setItem('user_name', name1);
    window.localStorage.setItem('user_email', name2);
    window.localStorage.setItem('user_password', password2);
    
   
    user_register(api_key,client_id,name1,name2,password2);
	
   

	});


function user_register(api_key,client_id,name1,name2,password){  
    var json_data_user_register = {
        "api_key":api_key,
		"client_id":client_id,
		"name":name1,
		"email":name2,
        "password":password
    };
var data_user_register = JSON.stringify(json_data_user_register);
console.log(data_user_register);
    //showLoader();
xhr = new XMLHttpRequest();
var url = "http://52.203.240.40:8080/user/register";

xhr.open("POST", url, true);
xhr.setRequestHeader("Content-type", "application/json");
xhr.setRequestHeader('Access-Control-Allow-Origin','*');
xhr.onreadystatechange = function () { 
    if (xhr.readyState == 4 && xhr.status >= 200) {
        var json = JSON.parse(xhr.responseText);
        if(xhr.status==200){
            window.location="./USER_LOGIN.html";
        }else{
        console.log(json);    
        }
        
        
        //hideLoader();
        }
}   
xhr.send(data_user_register);
}
