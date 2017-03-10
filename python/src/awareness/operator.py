from abc import ABCMeta, abstractproperty, abstractmethod
import misc
import ability as i_ability
import algorithm as i_algorithm
import backend as i_backend
import data as i_data
import protocol as i_protocol


class Operator:
    __metaclass__ = ABCMeta

    @abstractproperty
    def host(self):
        raise NotImplementedError()

    @abstractproperty
    def port(self):
        raise NotImplementedError()

    @abstractproperty
    def abilities(self):
        raise NotImplementedError()

    @abstractproperty
    def backend(self):
        raise NotImplementedError()

    @abstractproperty
    def protocol(self):
        raise NotImplementedError()


    @abstractmethod
    def profile(self):
        raise NotImplementedError()

    @abstractmethod
    def search(self, propagationLimit, trainingSet, testSet, progressCallback=None):
        raise NotImplementedError()

    @abstractmethod
    def process(self, index, inputSet, progressCallback=None):
        raise NotImplementedError()


class LocalOperator(Operator):

    host = ""
    port = -1
    abilities = []
    backend = None
    protocol = None

    algorithm = None
    assemblies = []
    remoteOperators = []


    def __init__(self, host="", port=1600, abilities = [], backend = None, protocol = None, algorithm = None, assemblies = [], remoteOperators = []):
        self.host = host
        self.port = port
        self.abilities = abilities
        self.backend = backend() if backend else i_backend.NativeBackend()
        self.protocol = protocol() if protocol else i_protocol.Protocol0()
        self.algorithm = algorithm() if algorithm else i_algorithm.DefaultAlgorithm()
        self.assemblies = assemblies
        self.remoteOperators = remoteOperators

        self.backend.processingAsync(self.protocol.provide, (self.backend.listen(host=host,port=port), self))


    def search(self, propagationLimit, trainingSet, testSet, progressCallback=None):
        self.algorithm.search(self.abilities, self.remoteOperators, trainingSet, testSet, progressCallback)

    def process(self, index, inputSet, progressCallback=None):
        return self.abilities[index].run(inputSet, progressCallback)

    def profile(self):
        profile = []

        for eachAbility in self.abilities:
            profile.append(eachAbility.profile)

        return profile


class RemoteOperator(Operator):

    host = ""
    port = -1
    abilities = []
    backend = None
    protocol = None

    connection = None

    def __init__(self, host, port, abilities = [], backend = None, protocol = None):
        self.host = host
        self.port = port
        self.abilities = abilities
        self.backend = backend() if backend else i_backend.NativeBackend()
        self.protocol = protocol() if protocol else i_protocol.Protocol0()
        if self.abilities == []:
            self.connect()
            self.retrieveAbilities()
            self.disconnect()

    def connect(self):
        self.connection = self.backend.connect(self.host, port=self.port)

    def disconnect(self):
        self.connection.close()
        self.connection = None

    def retrieveAbilities(self):
        acceptableData = self.protocol.getAcceptableData(self.connection)
        for i in range(len(acceptableData)):
            eachAcceptableData = acceptableData[i]
            newAbility = i_ability.RemoteAbility(self, i, eachAcceptableData[0], eachAcceptableData[1])

            self.abilities.append(newAbility)


    def search(self, propagationLimit, trainingSet, testSet, progressCallback=None):
        self.algorithm.search(self.connection, trainingSet, testSet, progressCallback)

    def process(self, index, inputSet, progressCallback=None):
        return self.abilities[index].run(inputSet, progressCallback)

    def profile(self):
        profile = []

        for eachAbility in self.abilities:
            profile.append(eachAbility.profile)

        return profile