const form = document.getElementById('form');

form.addEventListener('submit',function(e){
	e.preventDefault();
	
    const formdata = new FormData();
    let data= new FormData();
	//const input = document.getElementById('logo');
    const name1 = document.getElementById('name').value;
    const email1 = document.getElementById('email').value;
    const password1 = document.getElementById('password').value;
    const password2 = document.getElementById('password_confirm').value;
	
	// window.localStorage.setItem('name', name1);
	// window.localStorage.setItem('email', email1);
	//window.localStorage.setItem('password', password1);
    
	
	
	
	
	if(password1 == password2){
        //data.append("logo",input.files[0]);
        data.append("name",name1);
        data.append("email",email1);
	data.append("password",password1);

    }else{
        alert("Passowrd Not Matched-PLEASE TRY AGAIN");
    }
    var json;
    if(data!=null){
		fetch('http://52.203.240.40:8080/org/register', { // Your POST endpoint
    method: 'POST',
    mode:'cors',
    body: data // This is your file object
  }).then(
    response => response.json() // if the response is a JSON object
  ).then(
    success => alert("SUCCESFULLY REGISTERED ORGANISATION = " +  name1) // Handle the success response object
  ).catch(
    error => console.log(error) // Handle the error response object
  );
    }
    
    
	// data.forEach((value,key) => {
	// 	console.log(value)
    // 	 });
   
});
