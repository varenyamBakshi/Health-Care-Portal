var delbtns = document.getElementsByClassName('delete-product')

for(i=0;i<delbtns.length;i++){
    delbtns[i].addEventListener('click',function(){
        var ptd = this.dataset.product
        var act  = this.dataset.act 
        
        console.log('USER:', user)
        console.log('PTD:',ptd)
        console.log('ACT:',act)
        
        if(user == 'AnonymousUser'){
            console.log('user not auth')
        }else{
            Deleteproduct(ptd,act)
        }

    })
}


function Deleteproduct(ptd,act){

    var url = '/pharmacist/deleteproduct/'

    fetch(url,{
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'product':ptd,'act':act})
    })

    .then((response)=>{
        return response.json();
    })

    .then((data)=>{
        location.reload()
    });
}




var delbtns = document.getElementsByClassName('delete-product-pathology')

for(i=0;i<delbtns.length;i++){
    delbtns[i].addEventListener('click',function(){
        var ptd = this.dataset.product
        var act  = this.dataset.act 
        
        console.log('USER:', user)
        console.log('PTD:',ptd)
        console.log('ACT:',act)
        
        if(user == 'AnonymousUser'){
            console.log('user not auth')
        }else{
            Deleteproductpa(ptd,act)
        }

    })
}


function Deleteproductpa(ptd,act){

    var url = '/pathologist/removeproduct/'

    fetch(url,{
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'product':ptd,'act':act})
    })

    .then((response)=>{
        return response.json();
    })

    .then((data)=>{
        location.reload()
    });
}












