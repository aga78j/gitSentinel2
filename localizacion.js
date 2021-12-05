class Localizacion{

    constructor(callback){
        if (navigator.geolocation){
            //Obtenemos ubicacion
            navigator.geolocation.getCurrentPosition((position)=>{
                this.latitude= position.coords.longitude;
                this.longitud= position.coords.longitude;

                callback();
            });
        }else{
            alert("Tu navegador no soporta geolocalizacion!! :( ")
        }

    }

}