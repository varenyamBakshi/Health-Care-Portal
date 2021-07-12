var updateBtns = document.getElementsByClassName('deliver-order')

for(i=0;i<updateBtns.length;i++){
    updateBtns[i].addEventListener('click',function(){
        var orderId = this.dataset.order
        console.log('USER:', user)
        if(user == 'AnonymousUser'){
            console.log('user not auth')
        }else{
            deliverorder(orderId)
        }
    
    })
}

function deliverorder(orderId){
    

    var url='/pharmacist/deliverorder/'

    fetch(url,{
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'orderId':orderId})
    })

    .then((response) => {
        return response.json();
    })

    .then((data)=>{     
        location.reload()
    });
}









var updateBtns = document.getElementsByClassName('deliver-order-pathology')

for(i=0;i<updateBtns.length;i++){
    updateBtns[i].addEventListener('click',function(){
        var orderId = this.dataset.order
        console.log('USER:', user)
        if(user == 'AnonymousUser'){
            console.log('user not auth')
        }else{
            deliverorderpath(orderId)
        }
    
    })
}

function deliverorderpath(orderId){
    

    var url='/pathologist/ekart/'

    fetch(url,{
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'orderId':orderId})
    })

    .then((response) => {
        return response.json();
    })

    .then((data)=>{     
        location.reload()
    });
}


