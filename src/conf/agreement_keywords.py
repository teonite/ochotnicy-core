# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

from django.conf import settings


def agreement_get_keywords(*args, **kwargs):
    dict = {
        'media_root': settings.MEDIA_ROOT,
        'static_root': settings.STATIC_ROOT,

        #umowa
        'data_rozpoczecia_umowy': kwargs['offer'].agreement_stands_from,
        'data_zakonczenia_umowy': kwargs['offer'].agreement_stands_to,
        'zadania': kwargs['tasks'].body,

        #oferta
        'tytul_oferty': kwargs['offer'].title,
        'data_publikacji_oferty': str(kwargs['offer'].publish_from),
        'data_konca_waznosci_oferty': str(kwargs['offer'].publish_to),
        'maksymalna_liczba_wolontariuszy': kwargs['offer'].volunteer_max_count,
        'adres_logo_oferty': kwargs['offer_thumbnails'][0].filename if len(kwargs['offer_thumbnails']) > 0 else False,

        #wolontariusz
        'nr_telefonu_wolontariusza': kwargs['volunteer'].phonenumber,
        'wyksztalcenie_wolontariusza': kwargs['volunteer'].education.name,
        'plec_wolontariusza': kwargs['volunteer'].gender,
        'nazwa_uzytkownika_wolontariusza': kwargs['volunteer_user'].username,
        'imie_wolontariusza': kwargs['volunteer_user'].first_name,
        'nazwisko_wolontariusza': kwargs['volunteer_user'].last_name,
        'email_wolontariusza': kwargs['volunteer_user'].email,
        'data_urodzenia_wolontariusza': str(kwargs['volunteer'].birthday),
        'pesel_wolontariusza': kwargs['volunteer'].pesel,
        'nr_domu_wolontariusza': kwargs['volunteer'].house_number,
        'nr_mieszkania_wolontariusza': kwargs['volunteer'].apartment_number,
        'ulica_wolontariusza': kwargs['volunteer'].street,
        'kod_pocztowy_wolontariusza': kwargs['volunteer'].zipcode,
        'miasto_wolontariusza': kwargs['volunteer'].city,
        'kraj_wolontariusza': kwargs['volunteer'].country.name,
        'nr_dowodu_wolontariusza': kwargs['volunteer'].proof_number,

        #organizacja
        'nazwa_organizacji': kwargs['organization'].fullname,
        'typ_organizacji': kwargs['organization'].type.name,
        'krotka_nazwa_organizacji': kwargs['organization'].shortname,
        'nip_organizacji': kwargs['organization'].nip,
        'krs_organizacji': kwargs['organization'].krs,
        'nr_telefonu_organizacji': kwargs['organization'].phonenumber,
        'ulica_organizacji': kwargs['organization'].street,
        'nr_domu_organizacji': kwargs['organization'].house_number,
        'nr_mieszkania_organizacji': kwargs['organization'].apartment_number,
        'kod_pocztowy_organizacji': kwargs['organization'].zipcode,
        'dzielnica_organizacji': kwargs['organization'].district,
        'miasto_organizacji': kwargs['organization'].city,
        'wojewodztwo_organizacji': kwargs['organization'].province,
        'kraj_organizacji': kwargs['organization'].country,
        'adres_logo_organizacji': kwargs['org_thumbnails'][0].filename if len(kwargs['org_thumbnails']) > 0 else False,
    }

    for idx, signatory in enumerate(kwargs['signatories'], start=1):
        key = '{}_podpisujacego_nr_{}'
        dict[key.format('imie', idx)] = signatory.first_name
        dict[key.format('nazwisko', idx)] = signatory.last_name
        dict[key.format('stanowisko', idx)] = signatory.position

    return dict