import pexpect
import tempfile

def ssh(host, cmd, user, password, timeout=30, bg_run=False):                                                                                                 
    """SSH'es to a host using the supplied credentials and executes a command.                                                                                                 
    Throws an exception if the command doesn't return 0.                                                                                                                       
    bgrun: run command in the background"""                                                                                                                                    

    fname = tempfile.mktemp()                                                                                                                                                  
    fout = open(fname, 'w')                                                                                                                                                    

    options = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'                                                                         
    if bg_run:                                                                                                                                                         
        options += ' -f'                                                                                                                                                       
    ssh_cmd = 'ssh %s@%s %s "%s"' % (user, host, options, cmd)                                                                                                                 
    child = pexpect.popen_spawn(ssh_cmd, timeout=timeout)  #spawnu for Python 3                                                                                                                          
    child.expect(['[pP]assword: '])                                                                                                                                                                                                                                                                                               
    child.sendline(password)                                                                                                                                                    
    child.expect(pexpect.EOF)                                                                                                                                                  
    child.close()                                                                                                                                                              
    fout.close()                                                                                                                                                               

    fin = open(fname, 'r')                                                                                                                                                     
    stdout = fin.read()                                                                                                                                                        
    fin.close()                                                                                                                                                                

    if 0 != child.exitstatus:                                                                                                                                                  
        raise Exception(stdout)                                                                                                                                                

    return stdout

ssh('192.168.1.131', 'ping -c 4 www.google.com', 'pi', 'raspberry')