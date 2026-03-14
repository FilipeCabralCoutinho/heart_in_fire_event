document.querySelector("form").addEventListener("submit", function(event){

    const nome = document.querySelector('[name="nomeForm"]').value.trim()
    const cpf = document.querySelector('[name="cpfForm"]').value.trim()
    const cel = document.querySelector('[name="celForm"]').value.trim()
    const emergencia = document.querySelector('[name="emergencyContactForm"]').value.trim()
    const email = document.querySelector('[name="emailForm"]').value.trim()
    const remedy = document.querySelector('[name="remedyForm"]').value
    const hour = document.querySelector('[name="hourForm"]').value.trim()
    const fileInput = document.querySelector('[name="proofForm"]')

    // Name
    if(nome.length < 5){
        alert("Nome deve ter pelo menos 5 caracteres.")
        event.preventDefault()
        return
    }

    // CPF
    if(cpf.length !== 11){
        alert("CPF deve ter exatamente 11 números.")
        event.preventDefault()
        return
    }

    // Celphone
    if(cel.length < 10 || cel.length > 11){
        alert("Celular inválido.")
        event.preventDefault()
        return
    }

    // Emergency contact
    if(emergencia.length < 10 || emergencia.length > 11){
        alert("Contato de emergência inválido.")
        event.preventDefault()
        return
    }

    // Email
    if(!email.includes("@")){
        alert("Email inválido.")
        event.preventDefault()
        return
    }

    // Remedy
    if(remedy === "sim" && hour === ""){
        alert("Informe o horário do remédio.")
        event.preventDefault()
        return
    }

    // File
    if(fileInput.files.length === 0){
        alert("Envie o comprovante de pagamento.")
        event.preventDefault()
        return
    }

    const file = fileInput.files[0]
    const allowed = ["image/png","image/jpeg","application/pdf"]

    if(!allowed.includes(file.type)){
        alert("Arquivo inválido. Envie PDF, JPG ou PNG.")
        event.preventDefault()
        return
    }

})