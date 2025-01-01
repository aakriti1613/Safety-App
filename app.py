import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  Button,
  StyleSheet,
  Alert,
  TextInput,
  FlatList,
  TouchableOpacity
} from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import * as Location from 'expo-location';
import * as Linking from 'expo-linking';
import * as Contacts from 'expo-contacts';

const App = () => {
  const [location, setLocation] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [contacts, setContacts] = useState([]);
  const [deviceContacts, setDeviceContacts] = useState([]);

  useEffect(() => {
    (async () => {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setErrorMsg('Permission to access location was denied');
        return;
      }

      let loc = await Location.getCurrentPositionAsync({});
      setLocation(loc);
    })();

    (async () => {
      const { status } = await Contacts.requestPermissionsAsync();
      if (status === 'granted') {
        const { data } = await Contacts.getContactsAsync({ fields: [Contacts.Fields.PhoneNumbers] });
        setDeviceContacts(data);
      }
    })();
  }, []);

  const addContactFromDevice = (contact) => {
    if (contact?.phoneNumbers?.length > 0) {
      const phoneNumber = contact.phoneNumbers[0].number;
      setContacts((prev) => [...prev, phoneNumber]);
    } else {
      Alert.alert('Invalid Contact', 'This contact does not have a valid phone number.');
    }
  };

  const sendSOS = () => {
    if (!location) {
      Alert.alert('Location Error', 'Unable to fetch location. Please try again.');
      return;
    }

    const message = `SOS! I need help. My current location is: https://maps.google.com/?q=${location.coords.latitude},${location.coords.longitude}`;

    contacts.forEach((contact) => {
      Linking.openURL(`sms:${contact}?body=${encodeURIComponent(message)}`);
    });

    Alert.alert('SOS Sent', `Location: ${location.coords.latitude}, ${location.coords.longitude}`);
  };

  let locationText = 'Fetching location...';
  if (errorMsg) {
    locationText = errorMsg;
  } else if (location) {
    locationText = `Latitude: ${location.coords.latitude}, Longitude: ${location.coords.longitude}`;
  }

  const moveToCurrentLocation = () => {
    if (location && mapRef.current) {
      mapRef.current.animateToRegion({
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        latitudeDelta: 0.005,
        longitudeDelta: 0.005,
      }, 1000);
    } else {
      Alert.alert('Error', 'Unable to fetch current location.');
    }
  };

  const mapRef = React.createRef();

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Personal Safety App</Text>

      {/* Map Section */}
      <MapView
        ref={mapRef}
        style={styles.map}
        initialRegion={{
          latitude: location?.coords.latitude || 37.78825,
          longitude: location?.coords.longitude || -122.4324,
          latitudeDelta: 0.0922,
          longitudeDelta: 0.0421,
        }}
      >
        {location && (
          <Marker
            coordinate={{
              latitude: location.coords.latitude,
              longitude: location.coords.longitude,
            }}
            title="Your Location"
          />
        )}
      </MapView>

      <Button title="Move to Current Location" onPress={moveToCurrentLocation} color="#007bff" />

      {/* SOS Button */}
      <Button title="Send SOS" onPress={sendSOS} color="#d9534f" />

      {/* Location Text */}
      <Text style={styles.locationText}>{locationText}</Text>

      {/* Emergency Contacts */}
      <View style={styles.contactsContainer}>
        <Text style={styles.contactsHeader}>Emergency Contacts</Text>
        <FlatList
          data={contacts}
          keyExtractor={(item, index) => index.toString()}
          renderItem={({ item }) => <Text style={styles.contactItem}>{item}</Text>}
        />

        <Text style={styles.deviceContactsHeader}>Add from Device Contacts</Text>
        <FlatList
          data={deviceContacts}
          keyExtractor={(item, index) => index.toString()}
          renderItem={({ item }) => (
            <TouchableOpacity
              onPress={() => addContactFromDevice(item)}
              style={styles.deviceContactItem}
            >
              <Text>{item.name}</Text>
            </TouchableOpacity>
          )}
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f4f4f4',
  },
  header: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  map: {
    width: '90%',
    height: '40%',
    marginBottom: 20,
  },
  locationText: {
    marginTop: 10,
    fontSize: 16,
    color: '#333',
  },
  contactsContainer: {
    width: '90%',
    marginTop: 20,
    alignItems: 'center',
  },
  contactsHeader: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  deviceContactsHeader: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 20,
  },
  contactItem: {
    fontSize: 16,
    color: '#555',
    marginVertical: 5,
  },
  deviceContactItem: {
    padding: 10,
    backgroundColor: '#e9ecef',
    marginVertical: 5,
    borderRadius: 5,
    width: '100%',
  },
});

export default App;
