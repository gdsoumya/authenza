document.getElementById('register-form').addEventListener('submit',function(e){
	e.preventDefault();
	
	//const formdata1 = new FormData();
	let data1= new FormData();
    const name2 = document.getElementById('email').value;
    const name1=document.getElementById('name').value;
    const password2 = document.getElementById('pass').value;
 const api_key="2c80479a30ba47e880dfd7feedb48ba8";
    const client_id="9003a6ce2c77437baba5bb6f8e4ec9ae";
   // window.localStorage.setItem('api_key',api_key);
    //window.localStorage.setItem('client_id',client_id);
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
//xhr.setRequestHeader('Access-Control-Allow-Origin','*');
xhr.onreadystatechange = function () { 
    if (xhr.readyState == 4 && xhr.status >= 200) {
        var json = JSON.parse(xhr.responseText);
        console.log(json);
        if(xhr.status==200){
            window.location="./Email_verify1.html";
        }else{
        swal("Error", json['error'], "error");   
        }
        
        
        //hideLoader();
        }
}   
xhr.send(data_user_register);
}
