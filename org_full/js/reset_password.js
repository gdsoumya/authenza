document.getElementById('form').addEventListener('submit',function(e){
	e.preventDefault();
	
	//const formdata1 = new FormData();
	let data1= new FormData();
    const name2 = document.getElementById('email').value;
    const code = document.getElementById('code').value;
    const pass =document.getElementById('password').value;


    //const name1=document.getElementById('your_pass').value;
    
   const api_key="82deabb8984e49fcbb6fd9f87ba86ae7";
    const client_id="e576cf00c97d4a92b4766d9ed8b1e642";
    //const token = localStorage.getItem('user_login_token');
    reset_password(name2,code,pass);
                    
	
});


function reset_password(name2,code,pass){  
    var json_data_org_reset_password = {
        
        "email":name2,
        "code":code,
        "password":pass
    };

var data_org_reset_password = JSON.stringify(json_data_org_reset_password);
console.log(data_org_reset_password);
    //showLoader();
xhr = new XMLHttpRequest();
var url = "http://52.203.240.40:8080/org/reset_password";

xhr.open("POST", url, true);
xhr.setRequestHeader("Content-type", "application/json");

//xhr.setRequestHeader('Access-Control-Allow-Origin','*');
xhr.onreadystatechange = function () { 
    if (xhr.readyState == 4 && xhr.status >= 200) {
        var json = JSON.parse(xhr.responseText);
        console.log(json);
     if(xhr.status==200){
     alert("SUCCESS")
        window.location="./org_login.html";
}
else if (xhr.status>=400){
    console.log("error");
}
}  
}
xhr.send(data_org_reset_password);
}



