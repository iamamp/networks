"""
File:           rdt.py
Language:       python3
authors:         aag5405@cs.rit.edu Aniket Giriyalkar
                amp3453@cs.rit.edu Ashish Paralkar

Description:    This program is an implementation of rdt 3.0 protocol.

"""

from pydispatch import dispatcher
import threading
import time
import hashlib
import random

ALICE_SIGNAL = 'alice_signal'
ALICE_SENDER = 'alice_sender'
BOB_SIGNAL = 'bob_signal'
BOB_SENDER = 'bob_sender'


class Alice:
    """
        The class Bob is the class that represents the rdt receiver.
        Alice procrastinates and replies to bob
    """

    def __init__(self):
        """
        Constructor of the Class Alice
        """
        print('alice instantiated')

        # is not capable of making thread wait..
        dispatcher.connect(self.alice_dispatcher_receive, signal=BOB_SIGNAL,
                           sender=BOB_SENDER)
        # print('alice extra line?')
        time.sleep(2)

    def alice_dispatcher_receive(self, message):
        """
        Function that is the heart of the receiver and performs all the required
        functionality from the rdt receiver
        :param message: packet received from the sender.
        :return: None
        """
        time.sleep(2)
        recvd = message.split(".")
        if recvd[1] == 'time-out':
            print('timeout occurred at Bob')


        print('alice has received message: '+message)

        # print('body')
        #print(recvd[1])

        m = hashlib.md5()
        m.update(recvd[1].encode("utf-8"))
        chk = str(int(m.hexdigest(), 16))[0:12]
        # print('chk calc is '+chk)

        # sender sent accurate message body.
        if chk == recvd[2] and recvd[1]!='corrupt'  :
            case = random.randrange(0,3)

            # case0 : send correct ACK
            if case == 0:
                dispatcher.send(message=recvd[0]+'.ACK', signal=ALICE_SIGNAL, sender=ALICE_SENDER)

            # case1 : send unreadable ACK, will prompt Bob to send same msg again.
            if case == 1:
                dispatcher.send(message='corrupt', signal=ALICE_SIGNAL, sender=ALICE_SENDER)

            # case 2: send timeout message. Bob will realise something's wrong and resend same pkt again
            if case == 2:
                dispatcher.send(message = 'time-out', signal = ALICE_SIGNAL, sender = ALICE_SENDER)

        # senders msg was corrupted. flip the seq# of recvd msg
        elif recvd[1] == 'corrupt':
            print('in alice case corrupt from bob')
            if str(recvd[0]) == '0':
                dispatcher.send(message='1' + '.ACK', signal=ALICE_SIGNAL, sender=ALICE_SENDER)
            else:
                dispatcher.send(message='0' + '.ACK', signal=ALICE_SIGNAL, sender=ALICE_SENDER)

        # timeout occurred at senders plc
        elif recvd[1]=='time-out': #note that timeout msg will be received with seq# of intended pkt, so ull need to flip
            print('in alice, case timeout at bob')
            if str(recvd[0]) == '0':
                dispatcher.send(message='1' + '.ACK', signal=ALICE_SIGNAL, sender=ALICE_SENDER)
            else:
                dispatcher.send(message='0' + '.ACK', signal=ALICE_SIGNAL, sender=ALICE_SENDER)


class Bob:
    """
    The class Bob is the class that represents the sender and performs all the
    required functionality of the rdt sender.
    """
    seq = 0
    message0 = "message 0 from Bob"
    #message0 = "Bob"
    #message1 = "Bob"
    message1 = "message 1 from Bob"
    messagec = "corrupt"
    messaget = "time-out"
    chk0 = 0
    chk1 = 0

    def __init__(self):
        """
        Constructor of the class Bob.
        """
        print('Bob instantiated')

        # Establish a connection with the receiver.
        dispatcher.connect(self.bob_dispatcher_receive, signal=ALICE_SIGNAL,
                           sender=ALICE_SENDER)

        # prepare the packet to send.
        m = hashlib.md5()
        m.update(self.message0.encode("utf-8"))
        self.chk0 = str(int(m.hexdigest(), 16))[0:12]
        print('bob sent '+self.message0)

        # Send the packet.
        dispatcher.send(message=str(self.seq)+'.'+self.message0+'.'+self.chk0,
                        signal=BOB_SIGNAL, sender=BOB_SENDER)

        time.sleep(2)
        # print('bob done sending')   #this line is never reached

    def bob_dispatcher_receive(self, message):
        """
        Function that is heart of the rdt sender.
        :param message:
        :return:
        """

        time.sleep(2)
        m = hashlib.md5()
        recvd = message.split('.')

        if recvd[0] == 'time-out':
            print('timeout occurred at Alice')
        else:
            print('bob has received message: {}'.format(message))


        # 3 cases, case 1, ack# matches current seq#, and success, send next pkt
        if recvd[0] == str(self.seq):
            case = random.randrange(0, 3)

            # randomized case to send correct msg, just flip seq num and send correct msg
            if case == 0:
                if self.seq == 0:
                    self.seq = 1
                    m.update(self.message1.encode("utf-8"))
                    self.chk1 = str(int(m.hexdigest(), 16))[0:12]
                    dispatcher.send(message=str(self.seq) + '.' +
                                    self.message1 + '.' + self.chk1,
                                    signal=BOB_SIGNAL, sender=BOB_SENDER)

                else:
                    self.seq = 0
                    m.update(self.message0.encode("utf-8"))
                    self.chk0 = str(int(m.hexdigest(), 16))[0:12]
                    dispatcher.send(message=str(self.seq) + '.' +
                                            self.message0 + '.' + self.chk0,
                                    signal=BOB_SIGNAL, sender=BOB_SENDER)


            # randomised case to send corrupt msg. also flip here
            elif case == 1:
                if self.seq == 0:
                    self.seq = 1
                    m.update(self.message1.encode("utf-8"))
                    self.chk1 = str(int(m.hexdigest(), 16))[0:12]
                    dispatcher.send(message=str(self.seq) + '.' +
                                    self.messagec + '.' + self.chk1,
                                    signal=BOB_SIGNAL, sender=BOB_SENDER)

                else:
                    self.seq = 0
                    m.update(self.message0.encode("utf-8"))
                    self.chk0 = str(int(m.hexdigest(), 16))[0:12]
                    dispatcher.send(message = str(self.seq) + '.' +
                                    self.messagec + '.' + self.chk0,
                                    signal=BOB_SIGNAL, sender=BOB_SENDER)
                    # end_timer = time.time()

            # randomised case to create timeout at bob, also flip here
            else:
                if self.seq == 0:
                    self.seq = 1
                    m.update(self.message0.encode("utf-8"))
                    self.chk1 = str(int(m.hexdigest(), 16))[0:12]
                    dispatcher.send(message = str(self.seq) + '.' +
                                    self.messaget + '.' + self.chk1,
                                    signal = BOB_SIGNAL, sender = BOB_SENDER)
                    # start_timer = time.time()
                else:
                    self.seq = 0
                    m.update(self.message0.encode("utf-8"))
                    self.chk0 = str(int(m.hexdigest(), 16))[0:12]
                    dispatcher.send(message = str(self.seq) + '.' +
                                              self.messaget + '.' + self.chk0,
                                    signal = BOB_SIGNAL, sender = BOB_SENDER)
                    # start_timer = time.time()

        # case 2 and 3, ack# doesnt match current seq#, OR corrupt ACK recd OR timeout occurred resend.
        elif (recvd[0] == ('time-out' or 'corrupt')) or recvd[0] != self.seq:
            case = random.randrange(0, 3)

            # randomized case to RESEND correct msg, no flip
            if case == 0:
                if self.seq == 0:
                    m.update(self.message0.encode("utf-8"))
                    self.chk0 = str(int(m.hexdigest(), 16))[0:12]
                    dispatcher.send(message=str(self.seq) + '.' +
                                            self.message0 + '.' + self.chk0,
                                    signal=BOB_SIGNAL, sender=BOB_SENDER)

                else:
                    m.update(self.message1.encode("utf-8"))
                    self.chk1 = str(int(m.hexdigest(), 16))[0:12]
                    dispatcher.send(message=str(self.seq) + '.' +
                                            self.message1 + '.' + self.chk1,
                                    signal=BOB_SIGNAL, sender=BOB_SENDER)


            # randomised case to RESEND msg, but yet its corrupted. no flip
            elif case == 1:
                if self.seq == 1:
                    m.update(self.message1.encode("utf-8"))
                    self.chk1 = str(int(m.hexdigest(), 16))[0:12]
                    dispatcher.send(message=str(self.seq) + '.' +
                                            self.messagec + '.' + self.chk1,
                                    signal=BOB_SIGNAL, sender=BOB_SENDER)

                else:
                    m.update(self.message0.encode("utf-8"))
                    self.chk0 = str(int(m.hexdigest(), 16))[0:12]
                    dispatcher.send(message=str(self.seq) + '.' +
                                            self.messagec + '.' + self.chk0,
                                    signal=BOB_SIGNAL, sender=BOB_SENDER)
                    # end_timer = time.time()

            # randomised case to create timeout at bob, no flip
            else:
                if self.seq == 1:
                    m.update(self.message1.encode("utf-8"))
                    self.chk1 = str(int(m.hexdigest(), 16))[0:12]
                    dispatcher.send(message=str(self.seq) + '.' +
                                            self.messaget + '.' + self.chk1,
                                    signal=BOB_SIGNAL, sender=BOB_SENDER)
                    # start_timer = time.time()
                else:
                    m.update(self.message0.encode("utf-8"))
                    self.chk0 = str(int(m.hexdigest(), 16))[0:12]
                    dispatcher.send(message=str(self.seq) + '.' +
                                            self.messaget + '.' + self.chk0,
                                    signal=BOB_SIGNAL, sender=BOB_SENDER)
                    # start_timer = time.time()

if __name__ == '__main__':
    alice_thread = threading.Thread(target=Alice)
    alice_thread.start()
    bob_thread = threading.Thread(target=Bob)
    bob_thread.start()
