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
        if line:
            vmIds.append(line.strip().decode('cp866'))

    virtMachines = []
    cmd = """ssh root@192.168.1.101 'vim-cmd vmsvc/getallvms' | awk -F[ '{print $1}' | sed 1d | awk '{$1=""; print $0}' | sed 's/[\t]*$//'"""
    getVirtMachines = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in getVirtMachines.stdout.readlines():
        if line:
            virtMachines.append(line.strip().decode('cp866'))

    runVms = []
    cmd = "esxcli --config /home/zinner/graduate-work/session.cfg vm process list"
    getRunVms = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in getRunVms.stdout.readlines()[0::8]:
        if line:
            runVms.append(line.strip().decode('cp866'))

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


def getSwitches():
    cmd = "vicfg-vswitch --config /home/zinner/graduate-work/session.cfg -l"
    getSwitchList = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    switch_list = []
    for line in getSwitchList.stdout.readlines():
        if line:
            switch_list.append(line.strip().decode('cp866'))
    return switch_list

def getVmPath(machine_id):
    cmd = """ssh root@192.168.1.101 'vim-cmd vmsvc/getallvms' | grep "^%s" | awk -F[ '{print $2}' | awk -F.vmx '{print "["$1".vmx"}'""" % machine_id
    getVmPath = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    machine_path = getVmPath.stdout.readline().decode('cp866').strip("\n")
    return machine_path


def saveOperation(cmd):
    cmd = """echo "%s" >> /home/zinner/graduate-work/operationHistory.list""" % cmd
    commandExec = subprocess.Popen(cmd, shell=True)


def getOperationHistory():
    file = open("/home/zinner/graduate-work/operationHistory.list", "r")
    operationHistory = file.readlines()
    file.close()
    operationHistory = operationHistory[::-1]
    operations = []
    operationHistoryList = []
    for line in operationHistory:
        if line:
            operations = re.split(r'   ', line)
            operationHistoryList.append(operations)

    for i in operationHistoryList:
        for j in i:
            print(j, " ")
        print("\n")
    return operationHistoryList


def clearOperationHistory():
    file = open("/home/zinner/graduate-work/operationHistory.list", "w")
    file.close()


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
                clearOperationHistory()
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
        operationHistory = getOperationHistory()
        return render_to_response('index.html', {'virt_states': vmStates, 'virt_ids': vmIds, 'username': auth.get_user(request).username, 'group': auth.get_user(request).groups.all()[0].name, 'operation_history': operationHistory}, context_instance=RequestContext(request))
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
def summary(request):
    if request.user.is_authenticated():
        machine_id = request.POST['machine_id']
        machine_name = request.POST['machine_name']
        machine_state = request.POST['machine_state']
        machine_path = getVmPath(machine_id).replace("[The Datastore] ", "").replace(" ", "\\ ").replace("(", "\\(").replace(")", "\\)")
        machine_path = "/vmfs/volumes/The\ Datastore/" + machine_path

        if request.is_ajax():
            summary = []
            cmd = """/home/zinner/graduate-work/summary.sh \"%s\"""" % machine_path
            print("cmd=",cmd)
            getSummary = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in getSummary.stdout.readlines():
                if line:
                    summary.append(line.decode('cp866'))
            return HttpResponse(get_template('index.html').render({'summary': summary, 'machine_state': machine_state}, request))
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
            op_name = "Power on virtual machine"
            cmd = op_name + "   " + machine_name + "   %s   %s" % (auth.get_user(request), datetime.now())
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
            op_name = "Power off virtual machine"
            cmd = op_name + "   " + machine_name + "   %s   %s" % (auth.get_user(request), datetime.now())
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
            op_name = "Suspend virtual machine"
            cmd = op_name + "   " + machine_name + "   %s   %s" % (auth.get_user(request), datetime.now())
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
            op_name = "Reset virtual machine"
            cmd = op_name + "   " + machine_name + "   %s   %s" % (auth.get_user(request), datetime.now())
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
            op_name = "Create virtual machine snapshot"
            cmd = op_name + "   " + machine_name + "   %s   %s" % (auth.get_user(request), datetime.now())
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
            op_name = "Revert to current snapshot"
            cmd = op_name + "   " + machine_name + "   %s   %s" % (auth.get_user(request), datetime.now())
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
            return HttpResponse(get_template('index.html').render({'has_snapshot': has_snapshot}, request))
    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))


@csrf_exempt
def deploy(request):
    if_dhcp = 0
    if_dns = 0
    if_file = 0
    if request.user.is_authenticated():
        topology_name = request.POST['topology_name']
        if 'if_dhcp' in request.POST:
            if_dhcp = 1
        if 'if_dns' in request.POST:
            if_dns = 1
        if 'if_file' in request.POST:
            if_file = 1

        topology_name = topology_name.replace(' ', '')
        topology_name = "SmallOffice"
        if request.is_ajax():
            cmd = """/home/zinner/graduate-work/deploy.sh %s %s %s %s""" % (topology_name, if_dhcp, if_dns, if_file)
            deployTopology = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            result = deployTopology.stdout.readlines().pop().decode('cp866')
            parser = re.search(r' = 1', result)
            if parser is not None:
                return HttpResponse("Congratilations! The topology was successfully deployed.")
    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))


@csrf_exempt
def switchmanager(request):
    switch_list = getSwitches()
    if request.is_ajax():
        return HttpResponse(get_template('index.html').render({'switch_list': switch_list}, request))
    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))


@csrf_exempt
def cpuuse(request):
    cmd = "/home/zinner/graduate-work/getCPU.sh"
    getCpuUse = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = getCpuUse.stdout.readline().decode('cp866')
    if request.is_ajax():
        return HttpResponse(get_template('index.html').render({'cpu_use': cpu_use}, request))
    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))


@csrf_exempt
def memoryuse(request):
    cmd = "/home/zinner/graduate-work/getMemory.sh"
    getMemUse = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = getMemUse.stdout.readline().decode('cp866')
    if request.is_ajax():
        return HttpResponse(get_template('index.html').render({'memory_use': memory_use}, request))
    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))


@csrf_exempt
def diskuse(request):
    cmd = "/home/zinner/graduate-work/getDisk.sh"
    getDiskUse = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = getDiskUse.stdout.readline().decode('cp866')
    if request.is_ajax():
        return HttpResponse(get_template('index.html').render({'disk_use': disk_use}, request))
    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))


@csrf_exempt
def networkuse(request):
    cmd = "/home/zinner/graduate-work/getNetwork.sh"
    getNetUse = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = getNetUse.stdout.readline().decode('cp866')
    if request.is_ajax():
        return HttpResponse(get_template('index.html').render({'network_use': network_use}, request))
    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))


@csrf_exempt
def addswitch(request):
    if request.user.is_authenticated():
        switch_name = request.POST['switch_name']
        cmd = """vicfg-vswitch --config /home/zinner/graduate-work/session.cfg -a \"%s\"""" % switch_name
        addSwitch = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = addSwitch.stdout.readlines()
        op_name = "Create virtual switch"
        cmd = op_name + "   " + switch_name + "   %s   %s" % (auth.get_user(request), datetime.now())
        saveOperation(cmd)
        if request.is_ajax():
            operationHistory = getOperationHistory()
            switch_list = getSwitches()
            return HttpResponse(get_template('index.html').render({'operation_history': operationHistory, 'switch_list': switch_list}, request))
    else:
        return redirect('/vsphclient/login/', context_instance=RequestContext(request))