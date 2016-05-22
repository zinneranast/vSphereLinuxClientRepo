from django.template import RequestContext
from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse
from django.contrib import auth
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template

from datetime import datetime, date, time
import subprocess
import re


def getVMs():
    vmIds = []
    cmd = """ssh root@192.168.1.101 'vim-cmd vmsvc/getallvms' | awk '{print $1}' | sed 1d"""
    getVmIds = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in getVmIds.stdout.readlines():
        line = line.strip()
        if line:
            vmIds.append(line.decode('cp866'))

    virtMachines = []
    cmd = """ssh root@192.168.1.101 'vim-cmd vmsvc/getallvms' | awk -F[ '{print $1}' | sed 1d | awk '{$1=""; print $0}' | sed 's/[\t]*$//'"""
    getVirtMachines = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in getVirtMachines.stdout.readlines():
        line = line.strip()
        if line:
            virtMachines.append(line.decode('cp866'))

    runVms = []
    cmd = "esxcli --config /home/zinner/graduate-work/session.cfg vm process list"
    getRunVms = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in getRunVms.stdout.readlines()[0::8]:
        line = line.strip()
        if line:
            runVms.append(line.decode('cp866'))

    vmStates = {}
    vmId = {}
    k = 0
    for i in virtMachines:
        for j in runVms:
            if i == j:
                vmStates[virtMachines[k]] = 'Powered on'  
                break
            else:
                # cmd = """ssh root@192.168.1.101 'vim-cmd vmsvc/power.getstate %s'""" % vmIds[k]
                # getVmState = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                # vmState = getVmState.stdout.readlines()[1].decode('cp866')
                # parser = re.search(r'Powered off', vmState)
                # if parser is not None:
                vmStates[virtMachines[k]] = 'Powered off'
                # else:
                #     vmStates[virtMachines[k]] = 'Suspend'              
                # break
        vmId[virtMachines[k]] = vmIds[k]
        k += 1

    return vmStates, vmId


def getVmPath(machine_id):
    cmd = """ssh root@192.168.1.101 'vim-cmd vmsvc/getallvms' | grep "^%s" | awk -F[ '{print $2}' | awk -F.vmx '{print "["$1".vmx"}'""" % machine_id
    getVmPath = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    machine_path = getVmPath.stdout.readline().decode('cp866').strip("\n")
    return machine_path


# def getVmName(machine_id):
#     cmd = """ssh root@192.168.1.101 'vim-cmd vmsvc/getallvms' | grep "^%s" | awk -F[ '{print $1}' | awk '{$1=""; print $0}' | sed 's/[\t]*$//'""" % machine_id
#     getVmName = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     machine_name = getVmName.stdout.readline().decode('cp866').strip("\n")
#     return machine_name


def saveOperation(cmd):
    cmd = """echo "%s" >> /home/zinner/graduate-work/operationHistory.list""" % cmd
    commandExec = subprocess.Popen(cmd, shell=True)


def getOperationHistory():
    file = open("/home/zinner/graduate-work/operationHistory.list", "r")
    operationHistory = file.readlines()
    file.close()
    operationHistory = operationHistory[::-1]
    return operationHistory[:5]


def login(request):
    args = {}
    args.update(csrf(request)) 
    if request.POST:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            if user.groups.all()[0].name == "Blocked":
                return redirect('/vsphclient/blocked/', context_instance=RequestContext(request))
            else:
                return redirect('/vsphclient/index/', context_instance=RequestContext(request))
        else:
            args['login_error'] = "Invalid username or password."
            return render_to_response('login.html', args, context_instance=RequestContext(request))
    else:
        return render_to_response('login.html', args, context_instance=RequestContext(request))


def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return redirect('/vsphclient/login/', context_instance=RequestContext(request))


def index(request):
    if request.user.is_authenticated():
        vmStates, vmIds = getVMs()
        print(vmStates)
        return render_to_response('index.html', {'virt_states': vmStates, 'virt_ids': vmIds, 'username': auth.get_user(request).username, 'group': auth.get_user(request).groups.all()[0].name}, context_instance=RequestContext(request))
    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))


def home(request):
    if request.user.is_authenticated():
        return render_to_response('home.html', {'username': auth.get_user(request).username, 'group': auth.get_user(request).groups.all()[0].name}, context_instance=RequestContext(request))
    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))


def blocked(request):
    if request.user.is_authenticated():
        username = auth.get_user(request).username
        auth.logout(request)
        return render_to_response('blocked.html', {'username': username}, context_instance=RequestContext(request))
    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))


@csrf_exempt
def startmachine(request):
    if request.user.is_authenticated():
        machine_id = request.POST['machine_id']
        machine_name = request.POST['machine_name']
        cmd = """ssh root@192.168.1.101 'vim-cmd vmsvc/power.on %s'""" % machine_id
        startMachine = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = startMachine.stdout.readline().decode('cp866')
        parser = re.search(r'Powering on VM', result)
        if parser is not None:
            cmd = "Power on virtual machine - %s - %s - %s" % (machine_name, auth.get_user(request), datetime.now())
            saveOperation(cmd)
            if request.is_ajax():
                vmStates, vmIds = getVMs()
                operationHistory = getOperationHistory()
                return HttpResponse(get_template('index.html').render({'virt_states': vmStates, 'virt_ids': vmIds, 'operation_history': operationHistory}, request))
    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))


@csrf_exempt
def stopmachine(request):
    if request.user.is_authenticated():
        machine_id = request.POST['machine_id']
        machine_name = request.POST['machine_name']
        cmd = """ssh root@192.168.1.101 'vim-cmd vmsvc/power.off %s'""" % machine_id
        stopMachine = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = stopMachine.stdout.readline().decode('cp866')
        parser = re.search(r'Powering off VM', result)
        if parser is not None:
            cmd = "Power off virtual machine - %s - %s - %s" % (machine_name, auth.get_user(request), datetime.now())
            saveOperation(cmd)
            if request.is_ajax():
                vmStates, vmIds = getVMs()
                operationHistory = getOperationHistory()
                return HttpResponse(get_template('index.html').render({'virt_states': vmStates, 'virt_ids': vmIds, 'operation_history': operationHistory}, request))
    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))


@csrf_exempt
def suspendmachine(request):
    if request.user.is_authenticated():
        machine_id = request.POST['machine_id']
        machine_name = request.POST['machine_name']
        cmd = """ssh root@192.168.1.101 'vim-cmd vmsvc/power.suspend %s'""" % machine_id
        suspendMachine = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = suspendMachine.stdout.readline().decode('cp866')
        parser = re.search(r'Suspending VM', result)
        if parser is not None:
            cmd = "Suspend virtual machine - %s - %s - %s" % (machine_name, auth.get_user(request), datetime.now())
            saveOperation(cmd)
            if request.is_ajax():
                vmStates, vmIds = getVMs()
                operationHistory = getOperationHistory()
                return HttpResponse(get_template('index.html').render({'virt_states': vmStates, 'virt_ids': vmIds, 'operation_history': operationHistory}, request))
    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))


@csrf_exempt
def resetmachine(request):
    if request.user.is_authenticated():
        machine_id = request.POST['machine_id']
        machine_name = request.POST['machine_name']
        cmd = """ssh root@192.168.1.101 'vim-cmd vmsvc/power.reset %s'""" % machine_id
        resetMachine = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = resetMachine.stdout.readline().decode('cp866')
        parser = re.search(r'Reset VM', result)
        if parser is not None:
            cmd = "Reset virtual machine - %s - %s - %s" % (machine_name, auth.get_user(request), datetime.now())
            saveOperation(cmd)
            if request.is_ajax():
                vmStates, vmIds = getVMs()
                operationHistory = getOperationHistory()
                return HttpResponse(get_template('index.html').render({'virt_states': vmStates, 'virt_ids': vmIds, 'operation_history': operationHistory}, request))

    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))


@csrf_exempt
def takesnapshot(request):
    if request.user.is_authenticated():
        machine_id = request.POST['machine_id']
        machine_name = request.POST['machine_name']
        snapshot_name = request.POST['snapshot_name']
        snapshot_description = request.POST['snapshot_description']
        machine_path = getVmPath(machine_id)
        cmd = """vmware-cmd --config /home/zinner/graduate-work/session.cfg "%s" createsnapshot "%s" "%s" 0 1""" % (machine_path, snapshot_name, snapshot_description)
        createSnapshot = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = createSnapshot.stdout.readline().decode('cp866')
        parser = re.search(r'createsnapshot', result)
        if parser is not None:
            cmd = "Create virtual machine snapshot - %s - %s - %s" % (machine_name, auth.get_user(request), datetime.now())
            saveOperation(cmd)
            if request.is_ajax():
                operationHistory = getOperationHistory()
                return HttpResponse(get_template('index.html').render({'operation_history': operationHistory}, request))
    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))


@csrf_exempt
def revertsnapshot(request):
    if request.user.is_authenticated():
        machine_id = request.POST['machine_id']
        machine_name = request.POST['machine_name']
        machine_path = getVmPath(machine_id)
        cmd = """vmware-cmd --config /home/zinner/graduate-work/session.cfg "%s" revertsnapshot""" % machine_path
        revertSnapshot = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = revertSnapshot.stdout.readline().decode('cp866')
        parser = re.search(r'revertsnapshot', result)
        if parser is not None:
            cmd = "Revert to current snapshot - %s - %s - %s" % (machine_name, auth.get_user(request), datetime.now())
            saveOperation(cmd)
            if request.is_ajax():
                operationHistory = getOperationHistory()
                return HttpResponse(get_template('index.html').render({'operation_history': operationHistory}, request))
    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))


@csrf_exempt
def managersnapshot(request):
    if request.user.is_authenticated():
        machine_id = request.POST['machine_id']
        machine_name = request.POST['machine_name']
        machine_path = getVmPath(machine_id)
        cmd = """vmware-cmd --config /home/zinner/graduate-work/session.cfg "%s" hassnapshot""" % machine_path
        hasSnapshot = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = hasSnapshot.stdout.readline().decode('cp866')
        parser = re.search(r'1', result)
        if parser is not None:
            has_snapshot = "The virtual machine has already a snapshot."
        else:
            has_snapshot = "The virtual machine has not a snapshot."            
        if request.is_ajax():
            return HttpResponse(has_snapshot)
    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))

